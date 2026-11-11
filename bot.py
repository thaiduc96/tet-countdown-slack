import argparse
import fcntl
import json
import random
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo


TET_DATE = date(2027, 2, 6)
TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
APP_DIR = Path(__file__).resolve().parent
WEBHOOK_PATTERN = re.compile(
    r"https://hooks\.slack(?:-gov)?\.com/services/[A-Za-z0-9_-]+/"
    r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+"
)

MESSAGES = [
    "Deadline có thể trễ, nhưng Tết thì không! 😂",
    "Tết đang đến rất gần, lương tháng 13 đã đến chưa? 💸",
    "Mỗi ngày đi làm là một ngày gần lì xì hơn! 🧧",
    "Cố lên đồng đội! Bánh chưng đang chờ chúng ta! 🍃",
    "Tết này có người yêu chưa? Hay vẫn yêu công việc? 😂",
    "Bug có thể còn, nhưng Tết thì phải tới! 🐛",
    "Hôm nay làm việc chăm chỉ, Tết về ăn bánh chưng! 💪",
    "Không khí Tết đang loading... ⏳",
    "Tết đến nơi rồi, đừng để deadline đi theo về quê! 🚀",
    "Đi làm vì đam mê, mong Tết vì đam mê lớn hơn! 😆",
    "Tết là để sum vầy, không phải để fix bug! 🧑‍💻",
    "Mọi con đường đều dẫn về nhà, trừ đường tới production! 😂",
    "Chúc cả team một ngày ít bug, nhiều niềm vui! 🌸",
    "Lương có thể hết, nhưng niềm vui đón Tết thì còn! 🎊",
    "Tâm trí đã về quê, chỉ còn thân xác ở văn phòng! 🏠",
    "Tết sắp đến rồi, wishlist đã chuẩn bị xong chưa? 🎁",
    "Năm mới, mục tiêu mới, nhưng nhớ đóng task cũ nhé! 😎",
    "Cố thêm chút nữa, mùa bánh tét đang tới! 🍃",
    "Chưa thấy hoa mai, nhưng đã thấy mùi Tết rồi! 🌼",
    "Chúc mọi người code mượt, deploy êm, Tết an lành! ✨",
    "Việc hôm nay làm từng chút, niềm vui cuối năm gom từng ngày. 🌱",
    "Ai đã đặt vé về quê rồi thì xin chia sẻ chút bình tĩnh với cả team. 🚆",
    "Một buổi sáng ít họp đáng được bỏ vào phong bao lì xì. 🧧",
    "Chúc bạn tìm được chỗ ngồi cạnh cửa sổ trên chuyến xe về nhà. 🚌",
    "Người ta đếm cừu để ngủ. Mình đếm ngày để ăn bánh chưng. 🐑",
    "Nghe tiếng chổi quét sân là thấy nhà sắp có Tết. 🌿",
    "Một lời hỏi thăm cũng đủ làm ngày cuối năm ấm hơn. ☀️",
    "Mứt gừng hơi cay, còn tin nhắn báo nghỉ Tết thì ngọt. 🍬",
    "Hôm nay đóng được một task là dọn được một góc cho năm mới. ✅",
    "Tết về rồi, nhớ dành thời gian cho người hay hỏi ‘ăn cơm chưa?’. 🍚",
    "Cứ làm tốt phần mình hôm nay, phần còn lại để mai tính. 🌱",
    "Nếu có cuộc họp về mâm cỗ Tết, mình xin tình nguyện ghi biên bản. 🍲",
    "Mỗi lần dọn ngăn kéo cuối năm là một lần gặp lại chính mình hồi tháng Một. 📦",
    "Một cành mai, một ấm trà, một buổi sáng thong thả. 🌼",
    "Tự thưởng một khoảng nghỉ sau khi xong việc cũng là một kế hoạch hay. ☕",
    "Chúc team mở lịch hôm nay và thấy ít ô màu hơn dự kiến. 📆",
    "Cuối năm có hai thứ đi rất nhanh, thời gian và đĩa mứt dừa. 🥥",
    "Về nhà ăn một bữa cơm, nghe vài chuyện cũ kể lại vẫn thấy vui. 🏡",
    "Năm cũ còn vài trang, viết thêm một điều đáng nhớ nhé. 📖",
    "Chúc bạn gặp một người vui tính trên đường về quê. 🚉",
    "Inbox có thể đầy, vẫn còn chỗ cho một lời chúc. 💌",
    "Ước gì nút bỏ qua quảng cáo cũng áp dụng được cho đoạn chờ đến Tết. ⏩",
    "Hôm nay team mình có ai nghe nhạc xuân trước khi mở email chưa? 🎧",
    "Một góc bàn gọn gàng làm việc cuối năm nhẹ đi đôi chút. 🪴",
    "Chúc mọi người bàn giao gọn và nhớ mang sạc về quê. 🔌",
    "Cuối năm rồi, gửi một lời cảm ơn cho người từng giúp mình nhé. 💛",
    "Bánh tét cắt khoanh nào cũng tròn, mong ngày hôm nay cũng trọn vẹn như vậy. 🍃",
    "Ai phụ gói bánh nhớ tập buộc lạt trước khi nhận chỉ tiêu. 😄",
    "Tiếng xe ngoài ngõ ngày cận Tết nghe giống tiếng người sắp về nhà. 🏠",
    "Chúc bạn có thời gian uống cà phê khi ly còn nóng. ☕",
    "Dọn nhà cuối năm là dịp tìm lại món đồ đã mua thêm vì tưởng mất. 📦",
    "Cái ôm lúc vừa về tới cửa có khi là điều mình mong nhất cả năm. 🫂",
    "Nếu lịch trống được nửa tiếng, dành một chút để đi bộ cho thư thái nhé. 🌿",
    "Cả năm dùng chuông báo thức, Tết chỉ muốn thức dậy vì mùi đồ ăn. 🍳",
    "Hoa đào nở từ từ. Việc khó cũng cứ làm từng bước. 🌸",
    "Chúc bạn đặt vé thuận lợi, xếp đồ vừa vali và về nhà an toàn. 🧳",
    "Hôm nay ai đóng task sớm được quyền chọn bài nhạc mở đầu buổi chiều. 🎶",
    "Có dịp ghé chợ hoa thì đi chậm một chút để ngắm đủ các màu. 💐",
    "Đầu năm mong bình an, cuối năm nhớ hỏi thăm nhau. 🌼",
    "Muốn biết nhà ai có Tết sớm, cứ nhìn xem hũ dưa món đã mở chưa. 🥕",
    "Những việc đã làm xong xứng đáng được ghi lại trước khi mở danh sách mới. 📝",
    "Chúc cả team tìm được mốc bàn giao mà ai cũng thở phào. 🙌",
    "Thấy xe chở quất chạy ngang là tự nhiên muốn dọn nhà. 🍊",
    "Cuối năm, gọi về nhà sớm hơn thường lệ một chút cũng vui. 📞",
    "Việc hôm nay làm gọn, tối về bóc quýt đọc sách. 🍊",
    "Năm nay mong bàn ăn đông người và ai cũng có món mình thích. 🍽️",
    "Trà ngon nhất lúc có người ngồi uống cùng. 🫖",
    "Mình đã sẵn sàng nghỉ Tết, vali đang chờ được thông báo. 🧳",
    "Mong bạn mang về nhà nhiều chuyện vui để kể. 🏡",
    "Hôm nay cho phép mình vui vì một việc nhỏ đã làm xong nhé. ✨",
    "Ngày nào thấy mai nở trong thành phố, ngày đó nghe nhạc xuân hợp hẳn. 🌼",
    "Nếu phải xếp hàng mua đồ Tết, chúc bạn chọn đúng hàng chạy nhanh. 🛒",
    "Phong bao đẹp nhất là phong bao có người đề tên mình bằng tay. 🧧",
    "Ai còn nhớ lần đầu được giao canh nồi bánh chưng không? 🔥",
    "Chúc bạn hoàn thành việc khó nhất trước khi đồng nghiệp rủ đi ăn trưa. 🍜",
    "Có vài món chỉ ăn mỗi dịp Tết mà cả năm vẫn nhớ rõ vị. 🥢",
    "Ngày cuối năm, nhớ cảm ơn cả bản thân vì đã đi được tới đây. 🌷",
    "Chúc dự báo chuyến về nhà của bạn có nắng nhẹ và đường thông. 🚗",
    "Nồi thịt kho mà có thêm trứng thì ai cũng tự nhận mình ăn ít. 🍲",
    "Chúc team kết thúc ngày bằng tin nhắn ‘xong rồi nhé’. ✅",
    "Nếu chưa biết chúc gì, ‘mong năm tới bạn có nhiều ngày vui’ là đủ rồi. 💌",
    "Cuối năm rồi, để dành một buổi tối làm điều mình thích nhé. 🌙",
    "Dọn tủ lạnh trước Tết để có chỗ cho phần đồ ăn người nhà gói mang đi. 🍱",
    "Tết này thử chụp thêm một tấm ảnh cả nhà cùng vào khung hình. 📷",
    "Giữa bao việc cuối năm, mong bạn vẫn có một bữa trưa đàng hoàng. 🍚",
    "Một chiếc bánh chưng vuông vức rất có sức thuyết phục trong giờ đói. 😋",
    "Chúc bạn chốt được việc cần chốt và ngủ một giấc ngon. 🌙",
    "Ghé ngang chợ cuối năm, mua cho mình một bó hoa cũng được. 💐",
    "Chúc chuyến về quê có đủ chỗ cho hành lý và một túi quà nhỏ. 🎁",
]

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

# Thứ tự cố định giúp câu nói thay đổi mỗi ngày, kể cả khi chạy lại.
random.Random(2027).shuffle(MESSAGES)


def build_message(today):
    remaining = (TET_DATE - today).days
    if remaining < 0:
        return None
    if remaining == 0:
        return (
            "🎊 *CHÚC MỪNG NĂM MỚI ĐINH MÙI 2027!* 🐐\n\n"
            "🧧 *HÔM NAY LÀ MÙNG 1 TẾT!* 🧧\n\n"
            "Chúc cả team một năm mới sức khỏe, may mắn, hạnh phúc và thành công! 🌸\n"
            "✨ Chúc mọi người năm mới ít bug, nhiều bonus, mọi deadline đều suôn sẻ! 🥳"
        )

    if remaining == 1:
        title = "🎆 *HÔM NAY LÀ NGÀY GIAO THỪA. CÒN 1 NGÀY NỮA LÀ TẾT!*"
    elif remaining <= 7:
        title = f"🔥 *CHỈ CÒN {remaining} NGÀY NỮA LÀ TẾT!*"
    else:
        title = f"🧧 *CÒN {remaining} NGÀY NỮA LÀ TẾT!*"

    lines = [
        "🐐 *ĐẾM NGƯỢC TẾT ĐINH MÙI 2027* 🌸",
        "",
        title,
        "📅 Mùng 1 Tết: 06/02/2027",
        "",
        f"💬 _{MESSAGES[(remaining - 1) % len(MESSAGES)]}_",
    ]
    rng = random.Random(today.toordinal() + 2027)
    if rng.random() < 0.4:
        song = rng.choice(SONGS)
        url = "https://www.youtube.com/results?search_query=" + quote_plus(song)
        lines.extend(["", f"🎵 Nhạc Tết hôm nay: <{url}|{song}>"])
    if remaining <= 3:
        lines.extend(["", "🧳 Chuẩn bị hành lý và sẵn sàng về nhà thôi!"])
    lines.extend(["", "✨ Chúc cả team một ngày thật vui vẻ!"])
    return "\n".join(lines)


def send_slack(message):
    webhook_file = APP_DIR / "webhook"
    if not webhook_file.is_file():
        raise ValueError("Chưa có Slack Incoming Webhook. Hãy chạy ./install.sh.")
    url = webhook_file.read_text(encoding="utf-8").strip()
    if not WEBHOOK_PATTERN.fullmatch(url):
        raise ValueError("Webhook sai định dạng. Hãy chạy ./install.sh --replace-webhook.")

    payload = json.dumps(
        {"text": message, "unfurl_links": False, "unfurl_media": False},
        ensure_ascii=False,
    )
    # curl của macOS dùng chứng chỉ hệ thống. Đọc URL qua stdin để giữ bí mật
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
    parser = argparse.ArgumentParser(description="Bot Slack đếm ngược Tết Đinh Mùi 2027.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="in nội dung xem trước (mặc định)")
    mode.add_argument("--test-send", action="store_true", help="gửi một tin thử vào Slack")
    mode.add_argument("--scheduled", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--date", type=date.fromisoformat, help="ngày xem trước (YYYY-MM-DD)")
    args = parser.parse_args()
    if args.date and (args.scheduled or args.test_send):
        parser.error("--date chỉ dùng để xem trước.")

    now = datetime.now(TIMEZONE)
    if args.scheduled and (now.hour != 9 or now.date() > TET_DATE):
        return 0

    message = build_message(args.date or now.date())
    if message is None:
        print("Tết 2027 đã qua. Đã dừng thông báo.")
        return 0

    try:
        if args.scheduled:
            send_daily(now.date(), message)
        elif args.test_send:
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
