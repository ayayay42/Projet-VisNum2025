import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class Leaderboard:
    """
    Gère un fichier JSON contenant une liste d'entrées {name, score, date}.
    Par défaut le fichier est <repo_root>/leaderboard.json.
    """

    def __init__(self, path: Optional[str] = None):
        if path is None:
            # fichier placé à la racine du dépôt (deux niveaux au-dessus de utils/)
            self.path = Path(__file__).resolve().parents[1] / "leaderboard.json"
        else:
            self.path = Path(path)
        self._entries: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._entries, f, ensure_ascii=False, indent=2)

    def add(self, name: str, score: int) -> None:
        """
        Ajoute une entrée et enregistre le fichier JSON.
        Trie les scores en ordre décroissant après ajout.
        """
        entry = {
            "name": str(name),
            "score": int(score),
            "date": datetime.utcnow().isoformat() + "Z"
        }
        for e in self._entries:
            if e.get("name") == entry["name"] and e.get("score", 0) < entry["score"]:
                e["score"] = entry["score"]
                e["date"] = entry["date"]
                self._entries.sort(key=lambda e: e["score"], reverse=True)
                self._save()
                return
            if e.get("name") == entry["name"] and e.get("score", 0) > entry["score"]:
                return   
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e["score"], reverse=True)
        self._save()

    def get_all(self) -> List[Dict]:
        """Retourne toutes les entrées triées (score décroissant)."""
        return list(self._entries)

    def get_top(self, n: int = 10) -> List[Dict]:
        """Retourne les n meilleurs scores."""
        return self._entries[:n]

    def clear(self) -> None:
        """Supprime toutes les entrées (et met à jour le fichier)."""
        self._entries = []
        self._save()