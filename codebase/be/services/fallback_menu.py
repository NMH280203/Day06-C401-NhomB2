"""Thực đơn tĩnh khi LLM food_search lỗi — lọc theo bữa, budget, preferences, allergies, vị."""

from __future__ import annotations

from typing import Any

from models.schemas import FoodSuggestion

# Vị: cay, ngot, chua, man, beo (béo/đậm), nhat (thanh), dang (đắng nhẹ)
_FLAVOR_TAGS = frozenset({"cay", "ngot", "chua", "man", "beo", "nhat", "dang", "spicy", "sweet", "sour", "salty"})

# Mỗi món: meal_times, tags, flavors (vị), allergens
_FALLBACK_CATALOG: list[dict[str, Any]] = [
    {
        "name": "Phở bò tái",
        "category": "Món nước",
        "description": "Phở bò truyền thống, nước dùng trong",
        "estimated_price": 55000,
        "reason": "Dễ tìm quán, no vừa phải",
        "tags": ["popular", "no_spicy", "comfort"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Phở gà",
        "category": "Món nước",
        "description": "Phở gà thanh, nhẹ hơn phở bò",
        "estimated_price": 50000,
        "reason": "Phù hợp ăn nhẹ, không cay",
        "tags": ["light", "no_spicy", "healthy"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Bún chả Hà Nội",
        "category": "Bún",
        "description": "Thịt nướng than hoa, nước mắm chua ngọt",
        "estimated_price": 60000,
        "reason": "Đặc trưng miền Bắc, bữa trưa tối",
        "tags": ["popular", "local"],
        "flavors": ["chua", "ngot", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Bún thịt nướng",
        "category": "Bún",
        "description": "Bún tươi, thịt nướng, rau sống",
        "estimated_price": 45000,
        "reason": "Giá vừa, no nhanh",
        "tags": ["fast", "popular"],
        "flavors": ["ngot", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Bún bò Huế",
        "category": "Món nước",
        "description": "Bún bò cay đậm vị miền Trung",
        "estimated_price": 55000,
        "reason": "Thích vị đậm, cay",
        "tags": ["spicy", "local"],
        "flavors": ["cay", "man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm tấm sườn bì chả",
        "category": "Cơm",
        "description": "Sườn nướng, bì, chả trứng",
        "estimated_price": 50000,
        "reason": "No chắc, phổ biến Sài Gòn",
        "tags": ["popular", "fast"],
        "flavors": ["ngot", "man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm gà Hội An",
        "category": "Cơm",
        "description": "Cơm gà thơm, nước mắm gừng",
        "estimated_price": 48000,
        "reason": "Một người, vừa ngân sách",
        "tags": ["local", "no_spicy"],
        "flavors": ["man", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm niêu Singapore",
        "category": "Cơm",
        "description": "Cơm chiên hoặc cơm trắng kèm topping",
        "estimated_price": 65000,
        "reason": "Đổi gió so với cơm tấm",
        "tags": ["variety"],
        "flavors": ["man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Hủ tiếu Nam Vang",
        "category": "Món nước",
        "description": "Hủ tiếu khô hoặc nước, tôm thịt",
        "estimated_price": 45000,
        "reason": "Bữa sáng trưa nhẹ",
        "tags": ["popular"],
        "flavors": ["ngot", "man"],
        "meal_times": ["breakfast", "lunch"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Mì Quảng",
        "category": "Mì",
        "description": "Mì vàng, ít nước, topping đa dạng",
        "estimated_price": 50000,
        "reason": "Đặc sản miền Trung",
        "tags": ["local"],
        "flavors": ["man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["gluten", "hải sản", "tôm"],
    },
    {
        "name": "Bánh mì thịt nướng",
        "category": "Bánh",
        "description": "Bánh mì giòn, thịt nướng, pate",
        "estimated_price": 35000,
        "reason": "Nhanh, tiện mang đi",
        "tags": ["fast", "popular"],
        "flavors": ["man", "beo"],
        "meal_times": ["breakfast", "snack"],
        "allergens": ["gluten"],
    },
    {
        "name": "Bánh cuốn",
        "category": "Bánh",
        "description": "Bánh cuốn nóng, chả lụa, nước mắm",
        "estimated_price": 40000,
        "reason": "Bữa sáng thanh đạm",
        "tags": ["light", "no_spicy"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch"],
        "allergens": ["gluten"],
    },
    {
        "name": "Xôi xéo",
        "category": "Xôi",
        "description": "Xôi nếp, đậu xanh, hành phi",
        "estimated_price": 25000,
        "reason": "Sáng no, giá rẻ",
        "tags": ["vegetarian", "fast"],
        "flavors": ["man", "beo"],
        "meal_times": ["breakfast", "snack"],
        "allergens": [],
    },
    {
        "name": "Cháo lòng",
        "category": "Cháo",
        "description": "Cháo nóng, lòng heo, quẩy",
        "estimated_price": 40000,
        "reason": "Trời mưa lạnh rất hợp",
        "tags": ["comfort"],
        "flavors": ["man", "beo"],
        "meal_times": ["breakfast", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Cháo gà",
        "category": "Cháo",
        "description": "Cháo gà đơn giản, dễ tiêu",
        "estimated_price": 35000,
        "reason": "Nhẹ bụng, healthy",
        "tags": ["light", "healthy", "no_spicy"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Bún riêu cua",
        "category": "Bún",
        "description": "Riêu cua, cà chua, rau thơm",
        "estimated_price": 45000,
        "reason": "Món nước đậm đà",
        "tags": ["popular"],
        "flavors": ["chua", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "cua"],
    },
    {
        "name": "Bún mắm",
        "category": "Bún",
        "description": "Nước lèo mắm, topping đầy đủ",
        "estimated_price": 50000,
        "reason": "Vị miền Tây đặc trưng",
        "tags": ["local", "strong_flavor"],
        "flavors": ["man", "beo", "chua"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Gỏi cuốn tôm thịt",
        "category": "Gỏi",
        "description": "Cuốn tươi, chấm tương hoặc mắm nêm",
        "estimated_price": 40000,
        "reason": "Healthy, ít dầu",
        "tags": ["healthy", "light", "no_spicy"],
        "flavors": ["ngot", "nhat"],
        "meal_times": ["lunch", "dinner", "snack"],
        "allergens": ["tôm", "hải sản"],
    },
    {
        "name": "Nem nướng Nha Trang",
        "category": "Khai vị",
        "description": "Nem nướng, bánh tráng, rau sống",
        "estimated_price": 70000,
        "reason": "Nhóm bạn, chia sẻ",
        "tags": ["friends"],
        "flavors": ["ngot", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Lẩu thái chua cay",
        "category": "Lẩu",
        "description": "Nước lẩu chua cay, hải sản/rau",
        "estimated_price": 120000,
        "reason": "Nhóm 2–4 người, bữa tối",
        "tags": ["spicy", "friends", "variety"],
        "flavors": ["cay", "chua", "man"],
        "meal_times": ["dinner"],
        "allergens": ["hải sản", "tôm"],
    },
    {
        "name": "Lẩu bò nhúng dấm",
        "category": "Lẩu",
        "description": "Bò tươi, rau, bún kèm",
        "estimated_price": 150000,
        "reason": "No lâu, phù hợp tụ tập",
        "tags": ["friends", "family"],
        "flavors": ["chua", "man"],
        "meal_times": ["dinner"],
        "allergens": [],
    },
    {
        "name": "Bò kho bánh mì",
        "category": "Món nước",
        "description": "Bò kho nóng, ăn kèm bánh mì",
        "estimated_price": 55000,
        "reason": "Comfort food, trời mưa",
        "tags": ["comfort"],
        "flavors": ["ngot", "man", "beo"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Canh chua cá",
        "category": "Canh",
        "description": "Canh chua miền Tây, cá/lóc",
        "estimated_price": 80000,
        "reason": "Cơm nhà, vị chua thanh",
        "tags": ["family", "no_spicy"],
        "flavors": ["chua", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Cá kho tộ",
        "category": "Món mặn",
        "description": "Cá kho đậm đà, ăn với cơm trắng",
        "estimated_price": 70000,
        "reason": "Cơm nhà truyền thống",
        "tags": ["family", "local"],
        "flavors": ["ngot", "man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Đậu hũ sốt cà",
        "category": "Chay",
        "description": "Đậu hũ chiên hoặc luộc, sốt cà",
        "estimated_price": 40000,
        "reason": "Chay, healthy, giá mềm",
        "tags": ["vegetarian", "healthy", "no_spicy"],
        "flavors": ["chua", "man", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["đậu nành"],
    },
    {
        "name": "Phở chay",
        "category": "Chay",
        "description": "Phở nước rau củ, nấm",
        "estimated_price": 45000,
        "reason": "Chay, không thịt",
        "tags": ["vegetarian", "healthy"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Salad ức gà",
        "category": "Healthy",
        "description": "Rau xanh, ức gà, sốt nhẹ",
        "estimated_price": 65000,
        "reason": "Healthy, low carb",
        "tags": ["healthy", "light", "no_spicy"],
        "flavors": ["chua", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Poke bowl cá hồi",
        "category": "Healthy",
        "description": "Cơm/rau, cá hồi, trứng",
        "estimated_price": 95000,
        "reason": "Healthy, đổi gió",
        "tags": ["healthy", "variety"],
        "flavors": ["man", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "cá"],
    },
    {
        "name": "Bánh xèo miền Tây",
        "category": "Bánh",
        "description": "Xèo giòn, tôm thịt, rau sống",
        "estimated_price": 60000,
        "reason": "Đặc sản, chia nhóm",
        "tags": ["local", "friends"],
        "flavors": ["beo", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["tôm", "hải sản"],
    },
    {
        "name": "Chè đậu xanh",
        "category": "Tráng miệng",
        "description": "Chè mát, ngọt vừa",
        "estimated_price": 20000,
        "reason": "Snack sau bữa",
        "tags": ["vegetarian", "light"],
        "flavors": ["ngot"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Sinh tố bơ",
        "category": "Đồ uống",
        "description": "Sinh tố bơ đặc, no nhẹ",
        "estimated_price": 35000,
        "reason": "Xế trưa, không cần ngồi lâu",
        "tags": ["fast", "light"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack", "breakfast"],
        "allergens": ["sữa", "lactose"],
    },
    {
        "name": "Cà phê sữa đá + bánh mì",
        "category": "Sáng",
        "description": "Combo sáng Sài Gòn",
        "estimated_price": 30000,
        "reason": "Nhanh, rẻ",
        "tags": ["fast", "popular"],
        "flavors": ["ngot", "man"],
        "meal_times": ["breakfast", "snack"],
        "allergens": ["gluten", "lactose", "sữa"],
    },
    {
        "name": "Bún đậu mắm tôm",
        "category": "Bún",
        "description": "Đậu phụ, thịt, mắm tôm",
        "estimated_price": 55000,
        "reason": "Đặc trưng Hà Nội",
        "tags": ["local", "strong_flavor"],
        "flavors": ["man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["đậu nành", "tôm", "hải sản"],
    },
    {
        "name": "Miến gà",
        "category": "Miến",
        "description": "Miến nước gà, nhẹ",
        "estimated_price": 45000,
        "reason": "Không gluten (miến), thanh",
        "tags": ["light", "healthy"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Súp bí đỏ kem",
        "category": "Healthy",
        "description": "Súp ấm, ít cay",
        "estimated_price": 60000,
        "reason": "Trời mưa, healthy",
        "tags": ["healthy", "vegetarian", "no_spicy", "comfort"],
        "flavors": ["ngot", "beo", "nhat"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["lactose", "sữa"],
    },
    # ─── Món mới theo vị ─────────────────────────────────────────────────────
    {
        "name": "Bún ốc cay",
        "category": "Bún",
        "description": "Nước dùng ốc, sả, ớt, chua nhẹ",
        "estimated_price": 50000,
        "reason": "Thích vị cay chua, no vừa",
        "tags": ["spicy", "local"],
        "flavors": ["cay", "chua", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Mì cay Hàn (Tokbokki)",
        "category": "Mì",
        "description": "Bánh gạt cay ngọt, topping tùy chọn",
        "estimated_price": 75000,
        "reason": "Cay nồng, đổi gió",
        "tags": ["spicy", "variety"],
        "flavors": ["cay", "ngot", "man"],
        "meal_times": ["lunch", "dinner", "snack"],
        "allergens": ["gluten"],
    },
    {
        "name": "Gà rán cay Hàn",
        "category": "Gà",
        "description": "Gà giòn sốt gochujang cay ngọt",
        "estimated_price": 85000,
        "reason": "Cay ngọt đậm, nhóm bạn",
        "tags": ["spicy", "friends"],
        "flavors": ["cay", "ngot", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["gluten"],
    },
    {
        "name": "Lẩu mala Tứ Xuyên",
        "category": "Lẩu",
        "description": "Nước lẩu cay tê, thịt bò và rau",
        "estimated_price": 180000,
        "reason": "Cực cay, nhóm thích ăn cay",
        "tags": ["spicy", "friends", "variety"],
        "flavors": ["cay", "man", "beo"],
        "meal_times": ["dinner"],
        "allergens": [],
    },
    {
        "name": "Bánh tráng trộn",
        "category": "Ăn vặt",
        "description": "Bánh tráng, trứng cút, xoài, ớt",
        "estimated_price": 25000,
        "reason": "Snack cay chua, rẻ",
        "tags": ["fast", "popular"],
        "flavors": ["cay", "chua", "man"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Ốc len xào cay",
        "category": "Ốc",
        "description": "Ốc len sốt me ớt, chua cay",
        "estimated_price": 70000,
        "reason": "Quán ốc buổi tối",
        "tags": ["spicy", "friends"],
        "flavors": ["cay", "chua", "man"],
        "meal_times": ["dinner", "snack"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Chè thái",
        "category": "Tráng miệng",
        "description": "Trái cây, sữa dừa, đá bào",
        "estimated_price": 35000,
        "reason": "Ngọt mát, tráng miệng",
        "tags": ["light", "vegetarian"],
        "flavors": ["ngot"],
        "meal_times": ["snack"],
        "allergens": ["sữa", "lactose"],
    },
    {
        "name": "Chè ba màu",
        "category": "Tráng miệng",
        "description": "Đậu xanh, đậu đỏ, thạch, nước cốt dừa",
        "estimated_price": 25000,
        "reason": "Ngọt béo, giải nhiệt",
        "tags": ["vegetarian", "popular"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Bánh flan caramen",
        "category": "Tráng miệng",
        "description": "Flan mềm, caramen ngọt đậm",
        "estimated_price": 30000,
        "reason": "Tráng miệng ngọt",
        "tags": ["light"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": ["sữa", "lactose", "gluten"],
    },
    {
        "name": "Kem chiên",
        "category": "Tráng miệng",
        "description": "Kem lạnh bọc vỏ giòn",
        "estimated_price": 45000,
        "reason": "Ngọt lạ, ăn vui",
        "tags": ["variety"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": ["sữa", "lactose", "gluten"],
    },
    {
        "name": "Xôi ngọt lá cẩm",
        "category": "Xôi",
        "description": "Xôi tím, dừa nước, đậu xanh",
        "estimated_price": 20000,
        "reason": "Sáng ngọt no",
        "tags": ["vegetarian", "fast"],
        "flavors": ["ngot"],
        "meal_times": ["breakfast", "snack"],
        "allergens": [],
    },
    {
        "name": "Trà sữa trân châu",
        "category": "Đồ uống",
        "description": "Trà sữa ngọt, trân châu dai",
        "estimated_price": 40000,
        "reason": "Ngọt béo, cafe trà sữa",
        "tags": ["fast", "popular"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": ["sữa", "lactose"],
    },
    {
        "name": "Gỏi đu đủ Thái",
        "category": "Gỏi",
        "description": "Đu đủ bào, tôm khô, đậu phộng, nước mắm chua",
        "estimated_price": 55000,
        "reason": "Chua cay thanh, kích vị",
        "tags": ["spicy", "healthy", "light"],
        "flavors": ["chua", "cay", "man"],
        "meal_times": ["lunch", "dinner", "snack"],
        "allergens": ["hải sản", "tôm", "đậu nành"],
    },
    {
        "name": "Nem chua rán",
        "category": "Khai vị",
        "description": "Nem chua chiên giòn, chấm tương ớt",
        "estimated_price": 45000,
        "reason": "Chua cay giòn, nhâm nhi",
        "tags": ["friends", "fast"],
        "flavors": ["chua", "cay", "man"],
        "meal_times": ["lunch", "dinner", "snack"],
        "allergens": [],
    },
    {
        "name": "Nước chanh tuyết",
        "category": "Đồ uống",
        "description": "Chanh tươi, đá, chua ngọt",
        "estimated_price": 25000,
        "reason": "Giải khát chua mát",
        "tags": ["fast", "light"],
        "flavors": ["chua", "ngot"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Chè khoai môn",
        "category": "Tráng miệng",
        "description": "Khoai môn bùi, nước cốt dừa",
        "estimated_price": 22000,
        "reason": "Ngọt béo, ấm",
        "tags": ["vegetarian", "comfort"],
        "flavors": ["ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Kho quẹt",
        "category": "Món mặn",
        "description": "Thịt ba chỉ kho đậm, chấm rau sống",
        "estimated_price": 65000,
        "reason": "Mặn đậm, cơm nhà",
        "tags": ["family", "local"],
        "flavors": ["man", "ngot", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Cơm hến",
        "category": "Cơm",
        "description": "Hến xào, rau thơm, vị đậm Huế",
        "estimated_price": 40000,
        "reason": "Đặc sản miền Trung",
        "tags": ["local"],
        "flavors": ["man", "dang", "chua"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản"],
    },
    {
        "name": "Chả cá nướng",
        "category": "Hải sản",
        "description": "Chả cá thơm, chấm mắm ruốc",
        "estimated_price": 80000,
        "reason": "Mặn umami, cơm trắng",
        "tags": ["family", "local"],
        "flavors": ["man", "beo"],
        "meal_times": ["lunch", "dinner"],
        "allergens": ["hải sản", "cá"],
    },
    {
        "name": "Bún chả cá",
        "category": "Bún",
        "description": "Chả cá chiên, nước dùng trong",
        "estimated_price": 48000,
        "reason": "Thanh mặn, không cay",
        "tags": ["light", "no_spicy"],
        "flavors": ["man", "nhat"],
        "meal_times": ["breakfast", "lunch", "dinner"],
        "allergens": ["hải sản", "cá"],
    },
    {
        "name": "Sườn xào chua ngọt",
        "category": "Món mặn",
        "description": "Sườn non sốt cà chua, thơm",
        "estimated_price": 75000,
        "reason": "Chua ngọt cân bằng",
        "tags": ["family", "popular"],
        "flavors": ["chua", "ngot", "man"],
        "meal_times": ["lunch", "dinner"],
        "allergens": [],
    },
    {
        "name": "Dưa hấu muối ớt",
        "category": "Ăn vặt",
        "description": "Dưa hấu chấm muối ớt",
        "estimated_price": 15000,
        "reason": "Chua mặn cay nhẹ",
        "tags": ["fast", "light", "vegetarian"],
        "flavors": ["chua", "cay", "man"],
        "meal_times": ["snack"],
        "allergens": [],
    },
    {
        "name": "Bánh bò hấp",
        "category": "Bánh",
        "description": "Bánh bò mềm, ngọt thơm",
        "estimated_price": 20000,
        "reason": "Ngọt nhẹ, ăn sáng",
        "tags": ["vegetarian", "fast"],
        "flavors": ["ngot"],
        "meal_times": ["breakfast", "snack"],
        "allergens": ["gluten"],
    },
    {
        "name": "Cà phê đen đá",
        "category": "Đồ uống",
        "description": "Cà phê đen đậm, không sữa",
        "estimated_price": 20000,
        "reason": "Đắng nhẹ, tỉnh táo",
        "tags": ["fast"],
        "flavors": ["dang", "nhat"],
        "meal_times": ["breakfast", "snack"],
        "allergens": [],
    },
    {
        "name": "Matcha latte",
        "category": "Đồ uống",
        "description": "Trà matcha béo ngọt",
        "estimated_price": 45000,
        "reason": "Đắng ngọt hòa",
        "tags": ["variety"],
        "flavors": ["dang", "ngot", "beo"],
        "meal_times": ["snack"],
        "allergens": ["sữa", "lactose"],
    },
    {
        "name": "Bún thang",
        "category": "Bún",
        "description": "Bún nước trong, topping tinh tế",
        "estimated_price": 55000,
        "reason": "Thanh nhẹ, nhat",
        "tags": ["light", "no_spicy", "local"],
        "flavors": ["nhat", "man"],
        "meal_times": ["breakfast", "lunch"],
        "allergens": [],
    },
    {
        "name": "Lẩu cua đồng chua cay",
        "category": "Lẩu",
        "description": "Cua đồng, rau nhút, me ớt",
        "estimated_price": 160000,
        "reason": "Chua cay đậm, nhóm",
        "tags": ["spicy", "family", "friends"],
        "flavors": ["chua", "cay", "man"],
        "meal_times": ["dinner"],
        "allergens": ["hải sản", "cua"],
    },
]

_MEAT_KEYWORDS = (
    "thịt",
    "bò",
    "gà",
    "heo",
    "lợn",
    "sườn",
    "bì",
    "chả",
    "tôm",
    "cua",
    "cá ",
    "cá,",
    "hải sản",
    "lòng",
    "nem nướng",
    "bún chả",
    "bánh xèo",
)

_ALLERGY_ALIASES: dict[str, list[str]] = {
    "hải sản": ["hải sản", "tôm", "cua", "cá"],
    "tôm": ["tôm", "hải sản"],
    "cua": ["cua", "hải sản"],
    "cá": ["cá", "hải sản"],
    "gluten": ["gluten"],
    "lactose": ["lactose", "sữa"],
    "sữa": ["sữa", "lactose"],
    "đậu nành": ["đậu nành"],
    "chay": [],  # handled via vegetarian filter
}

# preference / câu user → vị trong catalog
_FLAVOR_PREF_MAP: dict[str, str] = {
    "cay": "cay",
    "spicy": "cay",
    "ớt": "cay",
    "ngot": "ngot",
    "sweet": "ngot",
    "ngọt": "ngot",
    "chua": "chua",
    "sour": "chua",
    "chua ngọt": "chua",
    "man": "man",
    "salty": "man",
    "mặn": "man",
    "beo": "beo",
    "rich": "beo",
    "béo": "beo",
    "đậm": "beo",
    "nhat": "nhat",
    "thanh": "nhat",
    "nhẹ": "nhat",
    "dang": "dang",
    "đắng": "dang",
}


def _dish_flavors(dish: dict[str, Any]) -> set[str]:
    explicit = {f.lower() for f in dish.get("flavors", [])}
    if explicit:
        return explicit
    tags = {t.lower() for t in dish.get("tags", [])}
    out = tags & _FLAVOR_TAGS
    if "spicy" in tags:
        out.add("cay")
    return out


def _normalize_flavor_prefs(preferences: list[str], user_text: str = "") -> set[str]:
    """Gom preference + từ khóa vị trong câu user."""
    out: set[str] = set()
    blob = " ".join(preferences or []).lower()
    if user_text:
        blob = f"{blob} {user_text.lower()}"
    for key, flavor in _FLAVOR_PREF_MAP.items():
        if key in blob:
            out.add(flavor)
    return out


def _normalize_allergies(allergies: list[str]) -> set[str]:
    out: set[str] = set()
    for a in allergies:
        key = a.strip().lower()
        out.add(key)
        if key == "chay":
            out.add("chay")
        for alias in _ALLERGY_ALIASES.get(key, [key]):
            out.add(alias)
    return out


def _looks_like_meat_or_seafood(dish: dict[str, Any]) -> bool:
    if "vegetarian" in dish.get("tags", []):
        return False
    name = dish.get("name", "").lower()
    if "chay" in name or "đậu hũ" in name or "xôi" in name:
        return False
    return any(kw in name for kw in _MEAT_KEYWORDS)


def _dish_conflicts_allergy(dish: dict[str, Any], user_allergies: set[str]) -> bool:
    dish_allergens = {a.lower() for a in dish.get("allergens", [])}
    if dish_allergens.intersection(user_allergies):
        return True
    # Chay / vegetarian: loại món có thịt, hải sản (trừ món gắn tag vegetarian)
    if "chay" in user_allergies or "vegetarian" in user_allergies:
        if "vegetarian" in dish.get("tags", []):
            return False
        non_veg = dish_allergens - {"gluten", "đậu nành", "lactose", "sữa"}
        if non_veg:
            return True
        if _looks_like_meat_or_seafood(dish):
            return True
    return False


def _score_dish(
    dish: dict[str, Any],
    *,
    meal_time: str,
    budget: int,
    preferences: list[str],
    weather: str,
    purpose: str,
    flavor_prefs: set[str] | None = None,
) -> float:
    score = 0.0
    if meal_time in dish.get("meal_times", []):
        score += 3.0
    price = int(dish.get("estimated_price", 0))
    if price <= budget:
        score += 2.0
    elif price <= budget * 1.15:
        score += 0.5
    else:
        score -= 2.0

    tags = set(dish.get("tags", []))
    prefs = set(preferences or [])
    score += len(tags.intersection(prefs)) * 1.2

    dish_flavors = _dish_flavors(dish)
    if flavor_prefs:
        overlap = dish_flavors.intersection(flavor_prefs)
        score += len(overlap) * 2.0
        if flavor_prefs and not overlap:
            score -= 0.8

    if weather in ("rain", "mưa", "rainy") and "comfort" in tags:
        score += 1.5
    if weather in ("hot", "nóng") and ("light" in tags or "healthy" in tags):
        score += 1.0

    if purpose == "family" and "family" in tags:
        score += 1.0
    if purpose in ("friends", "date") and ("friends" in tags or "variety" in tags):
        score += 0.8
    if purpose == "solo" and ("fast" in tags or "popular" in tags):
        score += 0.5

    if "no_spicy" in prefs and ("spicy" in tags or "cay" in dish_flavors):
        score -= 3.0
    if "healthy" in prefs and "healthy" in tags:
        score += 1.5
    if "vegetarian" in prefs and "vegetarian" in tags:
        score += 2.0

    return score


def pick_fallback_foods(
    *,
    meal_time: str = "lunch",
    budget: int = 80000,
    preferences: list[str] | None = None,
    allergies: list[str] | None = None,
    weather: str = "normal",
    purpose: str = "solo",
    limit: int = 5,
    user_text: str = "",
) -> list[dict]:
    """Chọn tối đa `limit` món từ catalog tĩnh."""
    prefs = list(preferences or [])
    user_allergy_set = _normalize_allergies(list(allergies or []))
    flavor_prefs = _normalize_flavor_prefs(prefs, user_text)

    candidates: list[tuple[float, dict[str, Any]]] = []
    for dish in _FALLBACK_CATALOG:
        if _dish_conflicts_allergy(dish, user_allergy_set):
            continue
        if int(dish.get("estimated_price", 0)) > budget * 1.25:
            continue
        s = _score_dish(
            dish,
            meal_time=meal_time,
            budget=budget,
            preferences=prefs,
            weather=weather,
            purpose=purpose,
            flavor_prefs=flavor_prefs,
        )
        if s > -1:
            candidates.append((s, dish))

    candidates.sort(key=lambda x: x[0], reverse=True)

    seen: set[str] = set()
    result: list[dict] = []
    for _, dish in candidates:
        name = dish["name"]
        if name in seen:
            continue
        seen.add(name)
        price = min(int(dish["estimated_price"]), budget)
        item = FoodSuggestion(
            name=name,
            category=dish["category"],
            description=dish["description"],
            estimated_price=price,
            reason=dish["reason"],
            tags=list(dish.get("tags", [])) + list(_dish_flavors(dish)),
        ).model_dump()
        result.append(item)
        if len(result) >= limit:
            break

    if len(result) < 3:
        for dish in _FALLBACK_CATALOG:
            if dish["name"] in seen:
                continue
            if _dish_conflicts_allergy(dish, user_allergy_set):
                continue
            price = min(int(dish["estimated_price"]), budget)
            result.append(
                FoodSuggestion(
                    name=dish["name"],
                    category=dish["category"],
                    description=dish["description"],
                    estimated_price=price,
                    reason=dish["reason"],
                    tags=list(dish.get("tags", [])) + list(_dish_flavors(dish)),
                ).model_dump()
            )
            seen.add(dish["name"])
            if len(result) >= limit:
                break

    return result
