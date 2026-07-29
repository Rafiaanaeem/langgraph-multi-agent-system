import insightface
from insightface.app import FaceAnalysis
import numpy as np
import torch
from typing import List, Dict, Any
from config import Config

class ArcFaceModel:
    def __init__(self):
        ctx_id = 0 if torch.cuda.is_available() else -1
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if ctx_id == 0 else ['CPUExecutionProvider']
        self.app = FaceAnalysis(name=Config.FACE_MODEL_NAME, providers=providers)
        self.app.prepare(ctx_id=ctx_id, det_size=Config.DET_SIZE)

    def extract(self, img_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """Detects faces, generates embeddings, and normalizes them for Cosine distance."""
        faces = self.app.get(img_bgr)
        results = []

        for idx, face in enumerate(faces):
            bbox = face.bbox.astype(int).tolist()
            embedding = face.embedding
            norm_emb = embedding / np.linalg.norm(embedding)
            results.append({
                "face_index": idx,
                "bbox": {"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]},
                "embedding": norm_emb.tolist()
            })
            
        return results
arcface = ArcFaceModel()