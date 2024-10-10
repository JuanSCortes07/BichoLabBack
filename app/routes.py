from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse
from app.models import Post, UserInsect, Comment, UserSignin
from app.database import get_database, get_bucket
from app.classification import VertexModel
from google.cloud.firestore import FieldFilter,ArrayUnion,ArrayRemove
import json
import requests
import time
from io import BytesIO

router = APIRouter()
VertexModel.vertex_init()

@router.post("/classify/")
async def classify_insect(image: UploadFile = File(...), db=Depends(get_database)):
    # Llamada a la API de Gemini para clasificar el insecto
    image_bytes: bytes = await image.read()
    insect_name = VertexModel.classification(image_bytes)

    # Verificar si ya existe en Firestore
    if insect_name == "Classification Fault":
        return {"message": "Classification Fault"}

    existing_insect= await db.collection("insects").where(filter=FieldFilter("taxonomy.specie","==",insect_name)).get()
    if existing_insect:
        print('retorne aqui')
        return {"_id":existing_insect[0].id, "data": existing_insect[0].to_dict()}
        
    
    # Obtener más datos si no está en la base de datos
    insect_data = VertexModel.get_insect_metadata(insect_name)
    result = requests.get('https://api.inaturalist.org/v1/observations', params={"quality_grade":"research","taxon_name":insect_name.lower(), "has[]":"photos","per_page":"1"}).json()['results'][0]['taxon']
    insect_photo = result['default_photo']['medium_url']
    print(insect_data)
    new_insect = json.loads(insect_data)
    new_insect["taxonomy"]["specie"] = insect_name
    new_insect["image"] = insect_photo
    result_add = await db.collection("insects").add(new_insect)
    added_insect_doc = await db.collection("insects").document(result_add[1].id).get()
    print('retorne aca')
    return {"_id":added_insect_doc.id, "data": added_insect_doc.to_dict()}
        

@router.post("/auth/signin")
async def auth_signin(user: UserSignin, db =Depends(get_database)):

    existing_user= await db.collection("users").where(filter=FieldFilter("username","==",user.username)).get()
    if existing_user:
        existing_user_dict = existing_user[0].to_dict()
        if user.password == existing_user_dict["password"]:
            return {"id": existing_user[0].id}
    
    return {"message":"SignIn error, We can't sign in you with this credentials"}

@router.post("/auth/signup")
async def auth_signin(user: UserSignin, db =Depends(get_database)):

    existing_user= await db.collection("users").where(filter=FieldFilter("username","==",user.username)).get()
    if existing_user:
        return {"message":"SignUp error, username is already in use"}
    
    user_ref = await db.collection("users").add(user.model_dump(mode='json'))
    return {"id": user_ref[1].id}


@router.post("/insects/upload/image/")
async def upload_insect_image(image: UploadFile = File(...), bucket = Depends(get_bucket)):
    #Leer imagen
    image_bytes: bytes = await image.read()

    #Cargar Storage y filename
    unique_blob_name = f"image_{int(time.time())}"
    blob = bucket.blob(unique_blob_name)

    #Subir Imagen
    blob.upload_from_string(image_bytes, content_type = image.content_type)

    image_name= blob.name

    return {"image_name": image_name}

@router.get("/insects/download/image/{image_name}")
async def download_insect_image(image_name: str, bucket = Depends(get_bucket)):
        
    blob = bucket.blob(image_name)
    # Descargar el contenido del blob
    try:
        image_bytes = blob.download_as_bytes()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")

    # Convertir el contenido de la imagen a un objeto BytesIO
    image_stream = BytesIO(image_bytes)
    return StreamingResponse(image_stream, media_type="image/jpeg")

@router.get("/insects/{insect_id}")
async def get_insect(insect_id: str, db=Depends(get_database)):
        
    existing_insect= await db.collection("insects").document(insect_id).get()
    if not existing_insect.exists:
        return {"message": "insect doesn't exists with this id"}
    
    return {"_id":insect_id,"data":existing_insect.to_dict()}

@router.post("/users/{user_id}/insects/add")
async def save_insect_for_user(user_id: str, user_insect: UserInsect, db=Depends(get_database)):
    
    # Guardar insecto en la lista del usuario
    insert_result = await db.collection("user_insects").add(user_insect.model_dump(mode='json'))
    user_insect_id = insert_result[1].id

    # Update the user's document to include the new insect ID
    await db.collection("users").document(user_id).update({
        "insects": ArrayUnion([user_insect_id])
    })
    return {"message": f"Insecto guardado exitosamente {user_insect_id}"}

@router.delete("/users/{user_id}/insects/delete")
async def delete_insect_for_user(user_id: str, user_insect_id: str, db=Depends(get_database)):
    # Eliminar insecto en la lista del usuario
    await db.collection("users").document(user_id).update({"insects": ArrayRemove([user_insect_id])})
    await db.collection("user_insects").document(user_insect_id).delete()
    return {"message": "Insecto eliminado exitosamente"}

@router.get("/users/{user_id}/insects/")
async def get_insects_for_user(user_id: str, db=Depends(get_database)):
    # Obtener el documento del usuario
    user_doc = await db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return {"error": "User not found"}

    # Obtener la lista de IDs de insectos del usuario
    user_data = user_doc.to_dict()
    user_insect_ids = user_data.get("insects", [])
    list_user_insects_db = [await db.collection("user_insects").document(user_insect_id).get() for user_insect_id in user_insect_ids]
    list_user_insects_dict = [{"_id":insect.id,"data":insect.to_dict()} for insect in list_user_insects_db if insect.exists]
    return list_user_insects_dict

@router.post("/forum/post/")
async def create_post(post: Post, db=Depends(get_database)):
    result = await db.collection("forum").add(post.model_dump(mode='json'))
    return {"post_id": str(result[1].id)}

@router.get("/forum/posts/")
async def get_posts(db=Depends(get_database)):
    results = db.collection("forum").stream()
    if not results:
        raise HTTPException(status_code=404, detail="No posts found.")
    return [{"_id":post.id, "data":post.to_dict()} async for post in results]

@router.get("/forum/{user_id}/posts/")
async def get_users_posts(user_id: str, db=Depends(get_database)):
    results = await db.collection("forum").where(filter=FieldFilter("author_id","==",user_id)).get()
    if not results:
        raise HTTPException(status_code=404, detail="No posts found for this user.")
    return [{"_id":post.id, "data":post.to_dict()} for post in results]

@router.delete("/forum/post/{post_id}/delete")
async def delete_post(post_id: str, db=Depends(get_database)):
    # Eliminar una publicación del foro
    result = await db.collection("forum").document(post_id).delete()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return {"message": "Post deleted successfully", "post_id": post_id}

@router.post("/forum/{post_id}/comments")
async def create_comment(post_id: str, comment: Comment, db=Depends(get_database)):
    await db.collection("forum").document(post_id).update({
        "comments": ArrayUnion([comment.model_dump(mode='json')])
    })
    return {"message": "Comentario publicacdo exitosamente"}