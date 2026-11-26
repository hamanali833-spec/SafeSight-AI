"""Shape of the analytics response."""
from app.schemas.alert import CamelModel


class Stats(CamelModel):
    total: int
    open: int
    open_high: int
    by_kind: dict[str, int]        # {"PPE": 5, "ZONE": 2}
    by_severity: dict[str, int]    # {"HIGH": 3, "PARTIAL": 4}
    by_camera: dict[str, int]      # {"warehouse": 2, "shop_grid_cam4": 5}
    by_hour: dict[str, int]        # {"20:00": 3, "21:00": 4}
