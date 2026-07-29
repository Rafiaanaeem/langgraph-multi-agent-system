import uuid
import cv2
import numpy as np
from config import Config

def extract_image_and_filename(file_item):
    """Safely decodes image bytes/dict/file object into OpenCV matrix and filename."""
    filename = "uploaded_image.jpg"
    contents = None

    if isinstance(file_item, dict):
        filename = file_item.get("filename", filename)
        contents = file_item.get("bytes")
    elif isinstance(file_item, bytes):
        contents = file_item
    elif hasattr(file_item, "read"):
        filename = getattr(file_item, "filename", filename)
        if hasattr(file_item, "seek"):
            try:
                file_item.seek(0)
            except Exception:
                pass
        contents = file_item.read()

    if not contents:
        return None, filename

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image, filename


class AddTool:
    def __init__(self, face_app, collection):
        self.app = face_app
        self.collection = collection

    async def execute(self, person_name: str, files: list):
        if not files:
            return {"success": False, "message": "No image file provided for enrollment."}
            
        image, filename = extract_image_and_filename(files[0])
        if image is None:
            return {"success": False, "message": "Uploaded file is empty or unreadable."}

        # Extract faces
        faces = self.app.extract(image)
        if len(faces) == 0:
            return {"success": False, "message": "No face detected in the image. Please upload a clear photo."}
        if len(faces) > 1:
            return {"success": False, "message": f"Found {len(faces)} faces in the image. Please provide a photo containing exactly 1 face for enrollment."}
        
        # Read face embedding & bounding box
        face_data = faces[0]
        embedding = face_data["embedding"]
        bbox_dict = face_data["bbox"]
        bbox = [bbox_dict["x1"], bbox_dict["y1"], bbox_dict["x2"], bbox_dict["y2"]]
        
        # Save to ChromaDB
        unique_id = f"{person_name.replace(' ', '_').lower()}_{uuid.uuid4().hex[:6]}"

        self.collection.upsert(
            ids=[unique_id],
            embeddings=[embedding],
            metadatas=[{"person_name": person_name.strip().title(), "bbox": str(bbox)}]
        )
        print(f"✅ [AddTool] Enrolled '{person_name}' (ID: {unique_id})")
        return {"success": True, "message": f"Successfully enrolled {person_name.title()} in the database."}


class SearchTool:
    def __init__(self, face_app, collection, threshold=None):
        self.app = face_app
        self.collection = collection
        self.threshold = threshold or Config.COSINE_THRESHOLD

    async def execute(self, files: list):
        if not files:
            return {"success": False, "message": "No images provided.", "results": []}

        print(f"📊 [SearchTool] Searching among {self.collection.count()} total vectors...")
        all_results = []
        
        for file_item in files:
            image, filename = extract_image_and_filename(file_item)
            if image is None:
                continue

            faces = self.app.extract(image)
            matches_for_this_image = []

            if len(faces) == 0:
                print(f"⚠️ No faces detected in {filename}")
            else:
                for idx, face_data in enumerate(faces):
                    query_embedding = face_data["embedding"]
                    bbox_dict = face_data["bbox"]
                    bbox = [bbox_dict["x1"], bbox_dict["y1"], bbox_dict["x2"], bbox_dict["y2"]]
                    
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=1,
                        include=["metadatas", "distances"]
                    )
                    
                    if results and results.get("distances") and len(results["distances"][0]) > 0:
                        distance = float(results["distances"][0][0])
                        matched_person = results["metadatas"][0][0]["person_name"]
                        
                        similarity_score = max(0.0, 1.0 - distance)
                        similarity_percent = round(similarity_score * 100, 1)

                        is_known = distance <= self.threshold
                        match_name = matched_person if is_known else "Unknown"
                    else:
                        distance = 1.0
                        similarity_percent = 0.0
                        match_name = "Unknown"
                        is_known = False
                        
                    matches_for_this_image.append({
                        "person_name": match_name, 
                        "is_known": is_known,
                        "cosine_distance": round(distance, 4),
                        "similarity_percent": similarity_percent,
                        "bbox": bbox
                    })
                    
            all_results.append({
                "filename": filename,
                "matches": matches_for_this_image
            })
            
        return {"success": True, "results": all_results}