import psutil

class CubaseProcessFinder:
    """Tìm tiến trình Cubase (theo danh sách tên giống code C#)."""

    CUBASE_NAMES = ["cubase", "cubase14", "cubase13", "cubase12", "cubasepro"]

    @staticmethod
    def find():
        # tìm chính xác
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                if name and any(name.lower().startswith(t) for t in CubaseProcessFinder.CUBASE_NAMES):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # fallback: tìm theo từ khóa "cubase"
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                if name and "cubase" in name.lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return None
