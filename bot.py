import argparse
import fcntl
import json
import os
import random
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo


COUNTDOWN_DAYS = 90
TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
APP_DIR = Path(__file__).resolve().parent
STEMS = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")
BRANCHES = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")
WEBHOOK_PATTERN = re.compile(
    r"https://hooks\.slack(?:-gov)?\.com/services/[A-Za-z0-9_-]+/"
    r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+"
)

COUNTDOWN_MESSAGES = {
    # 90–76 ngày. Tết còn xa, bắt đầu nghĩ xem mình mong chờ điều gì.
    90: "Còn khoảng ba tháng nữa là Tết. Mở lịch ngó mùng 1 một chút rồi quay lại với việc hôm nay thôi. 🗓️",
    89: "Có việc nào bạn muốn làm xong trước khi nghỉ Tết? Ghi lại một dòng hôm nay. Tới cuối năm mở ra xem cũng vui.",
    88: "Lịch họp vẫn dài hơn lịch nghỉ. Cứ thong thả, Tết đã có chỗ trên lịch rồi.",
    87: "Lần tới gọi về nhà, thử hỏi Tết này cả nhà định tụ họp hôm nào. Có khi nghe kể một hồi là thấy muốn về rồi.",
    86: "Vé xe, quà và lì xì cộng lại có thể hơi ngợp. Ước lượng từng khoản từ bây giờ rồi để dành dần sẽ dễ thở hơn.",
    85: "Tết này bạn mong điều gì hơn mọi năm? Có khi chỉ là một buổi sáng được dậy muộn và ngồi ăn sáng thật lâu.",
    84: "Hôm nào có bữa cơm vui, chụp lại một tấm. Cuối năm mở ra coi mới thấy những ngày bình thường cũng có nhiều chuyện hay.",
    83: "Hội bạn cũ có muốn gặp nhau dịp Tết thì nhắn từ bây giờ. Vẫn còn đủ thời gian cho cả nhóm trả lời ‘để xem lịch’.",
    82: "Có việc giấy tờ hay lịch hẹn muốn xong trước kỳ nghỉ thì chọn sẵn một ngày trong tháng này. Tới lúc bận, bạn sẽ mừng vì đã đặt lịch.",
    81: "Ai đón khách ở nhà dịp Tết có thể hỏi trước mọi người định ghé mùng mấy. Biết lịch rồi còn để dành được một ngày nghỉ cho mình.",
    80: "Nhắc tới Tết, nhà bạn nghĩ ngay đến món gì? Bánh tét, thịt đông hay cái hũ mứt lúc nào cũng vơi trước?",
    79: "Mấy ngày nghỉ Tết tới, bạn muốn đi đâu đó hay thích ở yên một chỗ? Nghĩ đến một ngày rảnh theo ý mình thôi cũng thấy vui.",
    78: "Thử để trống một buổi trong lịch cuối năm cho việc bạn thích. Một buổi sáng đi bộ hay đọc sách cũng đáng có hẹn.",
    77: "Hỏi thử mấy đứa nhỏ trong nhà đang mong điều gì nhất ở Tết. Có khi chúng chỉ mong được thức khuya với anh chị em họ.",
    76: "Tết còn hơn hai tháng. Giờ vẫn còn thong thả để nghĩ xem năm nay mình muốn giữ lại phong tục nào của nhà.",

    # 75–46 ngày. Lên lịch nghỉ, tính đường đi và đặt vé sớm.
    75: "Ai đi xa dịp Tết có thể mở thử lịch tàu, xe hoặc máy bay. Hôm nay khảo giá và ngó khung giờ là đủ.",
    74: "Nếu đi với người lớn tuổi, hỏi trước họ thích đi buổi nào. Một chuyến vừa giờ ăn, giờ ngủ sẽ dễ chịu hơn cho cả nhà.",
    73: "Nhóm bạn định góp một chuyến xe về quê thì chốt điểm đón sớm. Đến lúc ba người gửi ba vị trí khác nhau là biết vì sao. 📍",
    72: "Định xin nghỉ thêm một hai ngày quanh Tết thì trao đổi sớm với người làm cùng. Lúc lịch còn rộng rãi, mọi người dễ sắp xếp hơn.",
    71: "Khi so giá vé, tính luôn chặng từ bến hay sân bay về nhà. Có chuyến nhìn rẻ lắm cho tới khi mở bản đồ.",
    70: "Thử lưu lại hai chuyến bạn thấy hợp giờ và vừa túi tiền. Lúc cả nhà hỏi ‘chốt chuyến nào?’ sẽ có cái gửi ngay.",
    69: "Ai làm việc xuyên Tết có thể hẹn trước một buổi ăn cơm với người thân. Biết ngày gặp nhau rồi, chờ tới hôm đó cũng vui.",
    68: "Nhà có chó mèo mà bạn đi vắng vài ngày thì hỏi sớm người có thể ghé chăm. Mấy đứa ở nhà cũng cần có lịch Tết.",
    67: "Định mua quà chung cho bố mẹ hay ông bà thì hỏi anh chị em trước. Cả nhà sẽ đỡ có ba hộp bánh giống hệt nhau.",
    66: "Nếu đi xe nhà, tính thử số người và số vali. Nhớ chừa chỗ cho túi đồ ăn người nhà gói lúc quay lại.",
    65: "Ai ở lại thành phố dịp Tết có thể hẹn một buổi cà phê với người cũng ở lại. Phố vắng đi một chút, nói chuyện cũng thong thả hơn.",
    64: "Nếu lịch nghỉ vẫn đang chờ xác nhận, xem kỹ điều kiện đổi vé. Tới lúc đổi được ngày mà vẫn giữ được tiền thì nhẹ lòng hẳn.",
    63: "Canh vé chiều về quê rồi, nhớ ngó luôn chiều quay lại. Chọn chuyến sao cho còn một tối nghỉ ngơi trước khi mở máy đi làm.",
    62: "Hỏi ở nhà xem có món nào muốn bạn mang về từ chỗ đang sống. Có khi cả nhà chỉ nhờ đúng một món quen.",
    61: "Nếu chuyến bạn muốn đã mở bán và lịch nghỉ đã rõ, đây là lúc dễ chốt. Có vé trong tay, chờ Tết cũng khác hẳn. 🎫",
    60: "Còn hai tháng. Ai đã chốt ngày về, thử nhắn một câu ‘con có vé rồi’ cho người nhà. Từ đây sẽ có người đếm ngược cùng bạn.",
    59: "Lúc mua vé tàu hay máy bay, nhìn lại họ tên và ngày đi trước khi thanh toán. Mất vài giây để cả chuyến đi yên tâm hơn.",
    58: "Đi xe khách thì lưu luôn địa chỉ điểm đón và số nhà xe. Tới hôm đi, khỏi kéo vali tìm đúng cây xăng giữa một con đường dài.",
    57: "Lịch hai tháng tới nhìn còn rộng. Chọn sẵn một việc cần xong trước kỳ nghỉ để tới cuối năm khỏi nhớ ra cùng lúc với mười việc khác.",
    56: "Định gửi quà về xa thì hỏi người nhận hôm nào có nhà. Hẹn được ngày nhận đỡ phải nhờ cả xóm giữ giùm một thùng.",
    55: "Mở lại ảnh Tết năm ngoái thử xem. Có khi tấm cả nhà đứng lệch hàng mà ai cũng cười mới là tấm muốn giữ nhất.",
    54: "Ai định tự lái đường dài có thể chọn sẵn một buổi kiểm tra xe. Sát Tết còn đủ thứ để lo, bớt được một việc là mừng.",
    53: "Có người bạn lâu rồi chưa gặp thì thử nhắn hôm nay. Hẹn được một ly cà phê dịp Tết cũng có thêm một chuyện để chờ.",
    52: "Mỗi cuối tuần làm một việc chuẩn bị Tết là vừa. Tuần này xử lý một góc nhà thôi, còn sức đi ăn tối.",
    51: "Nhà có cái ghế lung lay hay vòi nước nhỏ giọt thì tranh thủ sửa một buổi. Tới lúc đông người, cái ghế vững sẽ có ích.",
    50: "Còn 50 ngày. Đủ gần để hỏi cả nhà muốn ăn gì dịp Tết và vẫn đủ xa để mọi người đổi ý vài lần.",
    49: "Ai định đi xa nhiều ngày có thể nhờ người tưới cây. Chậu cây còn xanh khi bạn quay lại là một lời chúc năm mới rất thiết thực. 🪴",
    48: "Nếu ở nhà hỏi ‘về muốn ăn gì?’, cứ nói một món bạn thực sự nhớ. Có khi món đó chỉ là canh chua với cá kho.",
    47: "Muốn chọn một món quà nhỏ mà hợp ý, thử nhớ xem người nhận từng nhắc gì. Một hộp trà đúng loại họ hay uống cũng đủ làm họ vui.",
    46: "Ai đón khách ngủ lại thì xem chăn gối và chỗ nằm từ giờ. Một cái ổ cắm cạnh giường cũng đáng giá lắm với người vừa đi xa.",

    # 45–31 ngày. Thử đồ, chọn quà và chuẩn bị nhà cửa.
    45: "Còn một tháng rưỡi. Thử phối một bộ đi chúc Tết từ đồ đang có. Biết mình thiếu gì rồi đi mua sẽ nhàn hơn.",
    44: "Ai muốn may hoặc sửa áo dài dịp Tết có thể hỏi lịch tiệm từ bây giờ. Vẫn còn thời gian thử cho vừa và đổi ý về màu.",
    43: "Có đôi giày mới định mang Tết thì đi thử một vòng. Hôm đi chúc Tết cả buổi, bàn chân sẽ cảm ơn bạn.",
    42: "Dọn thử ngăn kéo hay dùng nhất trước. Rất có thể bạn sẽ tìm lại món đồ đã cất ở chỗ ‘dễ nhớ lắm’.",
    41: "Còn mấy tuần để gói quà thong thả. Thử viết một tấm thiệp cho người lâu rồi bạn chưa gặp, kể một chuyện nhỏ của năm nay.",
    40: "Hỏi công thức món Tết hay ăn ở nhà. Nhớ hỏi kỹ đoạn người lớn bảo ‘nêm vừa miệng là được’.",
    39: "Ai định đặt bánh chưng, bánh tét ở chỗ quen thì hỏi hôm nào họ nhận đơn. Mở lời sớm để còn chọn được ngày lấy bánh.",
    38: "Mở hộp đồ trang trí năm ngoái xem trước khi đi mua. Dây đèn còn sáng, treo sang góc khác cũng thấy căn phòng mới hẳn.",
    37: "Lúc chọn quà cho cả nhà, nhớ đến người hay đứng bếp. Hôm nào cả nhà nấu cho họ ngồi ăn trước thì càng vui.",
    36: "Nhà nào thích làm mứt thì chọn một cuối tuần rảnh. Mẻ đầu tiên thường có cả đội kiểm tra chất lượng đứng quanh.",
    35: "Còn năm tuần. Nếu vẫn đang canh vé xe về quê, hỏi nhà xe về chỗ và giờ đón. Chốt được ghế rồi hẵng tính mang mấy túi.",
    34: "Sắp tới mùa ảnh Tết đầy nhóm chat. Ai còn giữ tấm hồi nhỏ mặc đồ mới đứng trước cửa nhà, giờ đem ra khoe được rồi.",
    33: "Đi thử đồ Tết nhớ thử cả ngồi xuống. Bộ đồ vừa đứng chụp ảnh lẫn ngồi ăn cỗ mới đáng đem về.",
    32: "Mua áo quần cho mấy đứa nhỏ thì hỏi cỡ trước. Từ Tết trước tới giờ, có bé đã cao thêm cả một đoạn tay áo.",
    31: "Dọn một ngăn tủ lạnh để chừa chỗ cho đồ Tết. Đây là dịp ăn nốt cái hộp bạn đã dời từ ngăn này sang ngăn kia.",

    # 30–16 ngày. Sắm Tết, chuẩn bị quà, đồ ăn và những cuộc hẹn.
    30: "Còn một tháng. Danh sách sắm Tết bắt đầu có áo quần, quà biếu, bánh mứt. Mua dần mấy món cần trước để tuần cuối còn thong thả.",
    29: "Lấy mấy phong bao lì xì năm ngoái còn dư ra xem. Cái đẹp nhất đôi khi nằm ngay dưới đáy ngăn kéo. 🧧",
    28: "Còn bốn tuần. Ai muốn tự làm dưa món hay củ kiệu thì xem trước công thức cần bao lâu. Có món ngon nhờ được ngâm từ sớm.",
    27: "Mua đồ mới rồi thì treo cả bộ lên cùng một chỗ. Tới sáng mùng 1 khỏi đi tìm cái thắt lưng khắp nhà.",
    26: "Nhà hay có khách ghé chơi có thể sắm trước trà, hạt và mứt. Mua vừa đủ để sau Tết còn muốn nhìn mặt hũ mứt.",
    25: "Thử dọn lối vào nhà hôm nay. Xếp lại giày dép, bỏ mấy cái thùng rỗng là đã có chỗ đón khách.",
    24: "Ai đang tính tiền lì xì có thể ghi ra số phong bao cần chuẩn bị. Đến tối giao thừa sẽ còn rảnh tay bóc quýt.",
    23: "Nếu định tặng đồ ăn tự làm, hỏi xem người nhận có kiêng món gì. Một hộp hợp khẩu vị vui hơn cả một giỏ đầy.",
    22: "Nhắn người thân hỏi bữa tất niên mỗi nhà định tổ chức hôm nào. Nếu trùng lịch, vẫn còn thời gian hẹn nhau một bữa trưa.",
    21: "Còn ba tuần. Mở lại tin nhắn xác nhận vé xem giờ khởi hành có thay đổi không. Biết sớm còn kịp báo người đưa đón.",
    20: "Ghé chợ thấy mấy sạp bắt đầu bày đồ đỏ, tự nhiên thấy Tết gần thật. Ai đi mua một món nhớ giữ lời với cái giỏ của mình.",
    19: "Nhà có người đi làm xa thì hỏi xem họ muốn được đón ở bến hay tự về. Một câu ‘tới nơi nhắn nha’ nghe đơn giản mà ấm.",
    18: "Quà đem theo lên xe thì thử xếp cùng vali. Hộp bánh giữ được nguyên góc khi tới nhà là một thành tựu. 🎁",
    17: "Chọn một việc dọn nhà làm trong 20 phút. Lau xong cửa kính hay xếp xong kệ sách là thấy nhà sáng hẳn.",
    16: "Ai còn quà hay thiệp cần gửi đi xa thì xem ngày giao dự kiến. Sát Tết, thùng hàng của mình cũng có một chuyến về quê.",

    # 15–8 ngày. Chốt việc, kiểm tra đồ đạc và chuẩn bị đi xa.
    15: "Còn nửa tháng. Chọn việc nào cần bàn giao trước khi nghỉ, rồi ghi rõ ai làm tiếp và file nằm ở đâu. Cả hai bên đều nhẹ đầu.",
    14: "Còn hai tuần. Thử hết bộ đồ định mặc mùng 1, kể cả giày và áo khoác. Tối giao thừa mới đi tìm nút áo thì hơi hồi hộp.",
    13: "Ai còn ca trực dịp Tết, hẹn sẵn một buổi gọi điện lúc mình rảnh. Nghe người nhà kể chuyện chuẩn bị Tết cũng vui lây.",
    12: "Ghi ra mấy món cần mua tươi vào những ngày cuối. Lúc chợ đông, danh sách ngắn giúp mình ra về trước khi tay đầy thêm ba túi.",
    11: "Nếu đã có tiền lẻ và phong bao, thử ghi tên lên mấy bao dễ nhầm. Sáng mùng 1 sẽ đỡ phải nhìn hai cái bao giống nhau rồi đoán.",
    10: "Mười ngày nữa. Lưu giờ mở cửa của tiệm hay mua đồ Tết. Đến nơi thấy cửa cuốn kéo xuống là hết hứng đi chợ.",
    9: "Ai sắp đi xa, gom giấy tờ, vé và sạc vào một túi dễ lấy. Hôm ra cửa chỉ cần nhớ đúng một chỗ.",
    8: "Dọn một góc để đặt bình hoa, cành đào hoặc chậu mai. Có người chỉ cần thay tấm khăn bàn là thấy phòng khách có Tết.",

    # 7–1 ngày. Về quê, ăn tất niên và đón giao thừa.
    7: "Còn đúng một tuần. Gửi nốt bàn giao, chúc đồng đội nghỉ vui rồi thở phào một cái. Tết bắt đầu thấy gần tới nơi rồi.",
    6: "Ai sắp về quê, nhắn người nhà giờ mình tới dự kiến. Có người nghe xong sẽ tính luôn nên để phần bạn món gì.",
    5: "Thử đóng vali một lượt. Để trống một góc cho đồ ăn lúc quay lại. Câu ‘mang một ít thôi’ ở nhà thường được đo bằng túi lớn.",
    4: "Nếu ghé chợ hoa hôm nay, đi chậm một chút. Nhìn quất, đào và mai xếp dọc lối đi là thấy đoạn đường về nhà khác hẳn. 🌼",
    3: "Ai đang trên đường về, chúc chuyến đi thuận lợi. Ai đã tới nhà, mong bạn kịp ngồi xuống ăn một bữa cơm nóng.",
    2: "Nhà nào gói bánh hôm nay, để người mới tập buộc thử một chiếc. Mấy cái bánh hơi méo thường có chuyện vui nhất để kể.",
    1: "Sáng cuối năm rồi. Chúc người đang đi đường sớm tới nơi và người còn trực có một ca yên ổn. Tối nay nhớ gọi cho người bạn muốn chúc Tết đầu tiên nhé.",
}


# Link tìm bài hát Tết trên YouTube
SONGS = [
    "Ngày Tết Quê Em - Từ Huy",
    "Đi Về Nhà - Đen x JustaTee",
    "Tết Này Con Sẽ Về",
    "Xuân Đã Về",
    "Ngày Xuân Long Phụng Sum Vầy",
    "Happy New Year - ABBA",
    "Một Năm Mới Bình An",
    "Tết Đong Đầy",
    "Phút Giao Thừa Lặng Lẽ",
    "Mùa Xuân Ơi",
]


def next_tet(today):
    with (APP_DIR / "tet-dates.txt").open(encoding="ascii") as dates:
        for line in dates:
            tet_date = date.fromisoformat(line.strip())
            if tet_date >= today:
                return tet_date
    return None


def build_message(today, tet_date):
    remaining = (tet_date - today).days
    if not 0 <= remaining <= COUNTDOWN_DAYS:
        return None
    year = tet_date.year
    year_name = f"{STEMS[(year - 4) % 10]} {BRANCHES[(year - 4) % 12]} {year}".upper()
    if remaining == 0:
        return (
            f"🎊 *CHÚC MỪNG NĂM MỚI {year_name}!* 🎊\n\n"
            "🧧 *HÔM NAY LÀ MÙNG 1 TẾT!* 🧧\n\n"
            "Chúc mọi người năm mới mạnh khỏe, có nhiều ngày vui và đủ thời gian cho những người mình thương.\n"
            "Mong sáng mùng 1 của bạn có một lời chúc ấm lòng và một tách trà được uống lúc còn nóng. 🌸"
        )

    if remaining == COUNTDOWN_DAYS:
        title = f"🧧 *BẮT ĐẦU ĐẾM NGƯỢC. CÒN {remaining} NGÀY NỮA LÀ TẾT!*"
    elif remaining == 1:
        title = "🎆 *HÔM NAY LÀ NGÀY GIAO THỪA. CÒN 1 NGÀY NỮA LÀ TẾT!*"
    elif remaining <= 7:
        title = f"🔥 *CHỈ CÒN {remaining} NGÀY NỮA LÀ TẾT!*"
    else:
        title = f"🧧 *CÒN {remaining} NGÀY NỮA LÀ TẾT!*"

    lines = [
        f"🧧 *ĐẾM NGƯỢC TẾT {year_name}* 🌸",
        "",
        title,
        f"📅 Mùng 1 Tết: {tet_date:%d/%m/%Y}",
        "",
        f"💬 _{COUNTDOWN_MESSAGES[remaining]}_",
    ]
    rng = random.Random(today.toordinal() + year)
    if rng.random() < 0.4:
        song = rng.choice(SONGS)
        url = "https://www.youtube.com/results?search_query=" + quote_plus(song)
        lines.extend(["", f"🎵 Nhạc Tết hôm nay: <{url}|{song}>"])
    return "\n".join(lines)


def send_slack(message):
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        webhook_file = APP_DIR / "webhook"
        if not webhook_file.is_file():
            raise ValueError("Chưa có Slack Incoming Webhook. Hãy cấu hình webhook trước khi gửi.")
        url = webhook_file.read_text(encoding="utf-8").strip()
    if not WEBHOOK_PATTERN.fullmatch(url):
        raise ValueError("Slack Incoming Webhook sai định dạng.")

    payload = json.dumps(
        {"text": message, "unfurl_links": False, "unfurl_media": False},
        ensure_ascii=False,
    )
    # curl dùng chứng chỉ hệ thống. Đọc URL qua stdin để giữ bí mật
    # khi xem danh sách tiến trình. --disable bỏ cấu hình curl cá nhân.
    result = subprocess.run(
        [
            "/usr/bin/curl", "--disable", "--silent", "--max-time", "15",
            "--header", "Content-Type: application/json",
            "--data-binary", payload, "--write-out", "\n%{http_code}",
            "--config", "-",
        ],
        input=f'url = "{url}"\n',
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode:
        raise ValueError(f"Lỗi kết nối khi gửi Slack (curl {result.returncode}).")
    body, _, status = result.stdout.rpartition("\n")
    if status != "200" or body.strip() != "ok":
        raise ValueError(f"Slack chưa xác nhận tin nhắn (HTTP {status}). Kiểm tra webhook và channel.")


def send_daily(today, message):
    last_sent = APP_DIR / "last-sent"
    with (APP_DIR / "send.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if last_sent.exists() and last_sent.read_text(encoding="utf-8").strip() == today.isoformat():
            return
        send_slack(message)
        pending = last_sent.with_suffix(".tmp")
        pending.write_text(today.isoformat() + "\n", encoding="utf-8")
        pending.replace(last_sent)
        print(f"Đã gửi thông báo ngày {today}.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Bot Slack đếm ngược Tết Nguyên đán hằng năm.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="in nội dung xem trước (mặc định)")
    mode.add_argument("--test-send", action="store_true", help="gửi một tin thử vào Slack")
    mode.add_argument("--scheduled", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--delivery-date", action="store_true", help=argparse.SUPPRESS)
    mode.add_argument("--send-date", type=date.fromisoformat, help=argparse.SUPPRESS)
    parser.add_argument("--date", type=date.fromisoformat, help="ngày xem trước (YYYY-MM-DD)")
    args = parser.parse_args()
    if args.date and (args.scheduled or args.test_send or args.delivery_date or args.send_date):
        parser.error("--date chỉ dùng để xem trước.")

    now = datetime.now(TIMEZONE)
    if args.scheduled and now.hour != 9:
        return 0

    today = args.date or now.date()
    if args.send_date and args.send_date != today:
        parser.error("Ngày gửi phải là ngày hiện tại theo giờ Việt Nam.")
    try:
        tet_date = next_tet(today)
        message = build_message(today, tet_date) if tet_date else None
        if args.delivery_date:
            if message:
                print(today.isoformat())
            return 0
        if args.scheduled or args.send_date:
            if message:
                send_daily(today, message)
            return 0

        if message is None:
            if tet_date:
                start = tet_date - timedelta(days=COUNTDOWN_DAYS)
                message = f"Mùa đếm ngược Tết {tet_date.year} bắt đầu ngày {start:%d/%m/%Y}."
            else:
                message = "Đã hết dữ liệu ngày Tết. Cập nhật tệp tet-dates.txt để tiếp tục."
        if args.test_send:
            send_slack("🧪 *Tin nhắn thử*\n\n" + message)
            print("Đã gửi tin nhắn thử vào Slack.")
        else:
            print(message)
    except (OSError, ValueError) as error:
        # Các lỗi của curl được chuyển thành thông báo không chứa URL.
        print(f"Lỗi: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
