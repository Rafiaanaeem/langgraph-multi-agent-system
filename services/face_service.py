import time
import uuid
from typing import List, Dict, Any
from fastapi import UploadFile

from models.model_loader import arcface
from services.chroma_service import chroma_db
from config import Config
from utils.image_utils import decode_image_bytes

class FaceService:
    
    @staticmethod
    async def enroll(person_name: str, files: List[UploadFile]) -> Dict[str, Any]:
        total_enrolled = 0
        details = []

        for file in files:
            contents = await file.read()
            img_bgr = decode_image_bytes(contents)
            faces = arcface.extract(img_bgr)

            if not faces:
                details.append({"filename": file.filename, "faces_found": 0, "status": "No face detected"})
                continue

            for face in faces:
                face_id = f"{person_name.replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
                metadata = {"person_name": person_name, "filename": file.filename}
                chroma_db.upsert_face(face_id, face["embedding"], metadata)
                total_enrolled += 1

            details.append({"filename": file.filename, "faces_found": len(faces), "status": "Enrolled"})

        return {
            "success": True,
            "message": f"Enrollment completed for {person_name}.",
            "total_faces_enrolled": total_enrolled,
            "details": details
        }

    @staticmethod
    async def search(files: List[UploadFile]) -> Dict[str, Any]:
        image_results = []

        for file in files:
            start_time = time.perf_counter()
            contents = await file.read()
            img_bgr = decode_image_bytes(contents)
            faces = arcface.extract(img_bgr)

            face_matches = []
            for face in faces:
                query_res = chroma_db.query_nearest(face["embedding"])
                distances = query_res.get("distances", [[]])[0]
                metadatas = query_res.get("metadatas", [[]])[0]

                if distances and metadatas:
                    cosine_dist = distances[0]
                    is_known = cosine_dist <= Config.COSINE_THRESHOLD
                    final_name = metadatas[0]["person_name"] if is_known else "Unknown"
                else:
                    cosine_dist = float("inf")
                    is_known = False
                    final_name = "Unknown"
                face_matches.append({
                    "face_index": face["face_index"],
                    "bounding_box": face["bbox"],
                    "person_name": final_name,
                    "cosine_distance": round(cosine_dist, 4) if cosine_dist != float("inf") else 1.0,
                    "is_known": is_known
                })

            image_results.append({
                "filename": file.filename,
                "faces_detected": len(faces),
                "matches": face_matches,
                "inference_time_sec": round(time.perf_counter() - start_time, 4)
            })

        return {
            "success": True,
            "total_images_processed": len(files),
            "results": image_results
        }