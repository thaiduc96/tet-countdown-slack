# Bot Slack đếm ngược Tết hằng năm

Mỗi năm, bot bắt đầu gửi lúc **09:00 giờ Việt Nam** vào ngày còn đúng **90 ngày** đến mùng 1 Tết. Bot gửi mỗi ngày, có tin riêng cho giao thừa và mùng 1, rồi tự chờ đến mốc 90 ngày của Tết năm sau. Tin nhắn xen kẽ câu vui, lời động viên và chuyện ngày Tết. Khoảng 40% số ngày có thêm liên kết tìm bài hát Tết trên YouTube.

Tệp `tet-dates.txt` chứa ngày mùng 1 Tết theo lịch âm Việt Nam từ **2026 đến 2199**. Bot đọc bảng này ngay trên Mac. Ví dụ, mùa Tết 2027 bắt đầu ngày 08/11/2026 và mùa Tết 2028 bắt đầu ngày 28/10/2027. [Dữ liệu lịch âm của Hồ Ngọc Đức](https://www.xemamlich.uhm.vn/JavaScript/)

## Chạy bằng GitHub Actions

1. Giải nén ZIP. Đưa toàn bộ mã nguồn, gồm thư mục ẩn `.github`, lên nhánh mặc định của repo riêng tư `thaiduc96/tet-countdown-slack`. Nếu dùng tên repo khác, cập nhật tên đầy đủ ở điều kiện `jobs.countdown.if` trong `.github/workflows/tet-countdown.yml`.
2. Vào **Settings → Secrets and variables → Actions → New repository secret**. Đặt tên secret là `SLACK_WEBHOOK_URL` và dán Slack Incoming Webhook của channel đích. [Tài liệu GitHub về repository secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
3. Vào **Actions → Tết Countdown → Run workflow**, chọn nhánh mặc định và chế độ `preview` để xem nội dung trong log. Chọn `send` khi muốn gửi tin đếm ngược thật của hôm nay. Lượt gửi tự động bắt đầu theo lịch khi workflow đã có trên nhánh mặc định và Actions đã bật.

Để tạo repo mới từ Terminal có GitHub CLI đã đăng nhập, chạy trong thư mục vừa giải nén:

```sh
git init -b main
git add .github .gitignore README.md bot.py tet-dates.txt install.sh uninstall.sh
git commit -m "Add annual Tet countdown bot"
gh repo create thaiduc96/tet-countdown-slack --private --source=. --push
gh secret set SLACK_WEBHOOK_URL --repo thaiduc96/tet-countdown-slack
```

Lệnh cuối sẽ hỏi URL trực tiếp. Nếu đã chạy LaunchAgent trên Mac và chuyển sang GitHub Actions cho cùng channel, chạy `./uninstall.sh` trên Mac để tránh hai nơi gửi cùng một ngày.

GitHub lên lịch lúc 09:00 giờ Việt Nam trong khoảng 23/10–20/02. Bot kiểm tra lại mốc 90 ngày trước khi gửi. Lượt chạy có thể trễ hoặc bị bỏ qua khi GitHub quá tải. Chế độ `send` có thể gửi bù trong ngày. Workflow lưu một dấu mốc sau khi Slack xác nhận để tránh gửi trùng khi chạy lại. Nếu cache đã bị xóa hoặc lượt chạy thất bại sau khi Slack nhận tin, kiểm tra channel trước khi chạy lại. [Tài liệu GitHub về lịch chạy](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## Cài đặt trên macOS

1. Kiểm tra Python bằng `python3 --version`. Cần **Python 3.10 trở lên**. Nếu cần cài Python, tải bộ cài cho macOS, rồi mở lại Terminal. Bot dùng thư viện chuẩn Python và `curl` có sẵn trên macOS. [Tải Python cho macOS](https://www.python.org/downloads/macos/)
2. Nếu đã có Slack Incoming Webhook cho channel đích, dùng lại URL đó. Để tạo mới, mở Slack API → **Your Apps** → **Create New App** → **From scratch** → **Incoming Webhooks**. Bật **Activate Incoming Webhooks**, chọn **Add New Webhook to Workspace**, chọn channel rồi bấm **Allow**. Với channel riêng tư, tài khoản tạo webhook cần là thành viên của channel đó. Sao chép Webhook URL. [Hướng dẫn của Slack](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/)
3. Mở Terminal trong thư mục mã nguồn `tet-countdown-slack` đã giải nén hoặc clone, rồi chạy:

   ```sh
   python3 bot.py --preview
   ./install.sh
   ```

   Dán Webhook URL tại lời nhắc trong Terminal và nhấn Enter. Terminal sẽ ẩn ký tự khi dán. Hãy chạy dưới tài khoản đang đăng nhập macOS. Bộ cài lưu webhook cục bộ với quyền `600`, trong thư mục `~/Library/Application Support/Tet Countdown` có quyền `700`.

Nếu đã cài bản chỉ chạy Tết 2027, chuẩn bị URL webhook rồi chạy `./uninstall.sh` từ thư mục **bản cũ** trước khi cài bản hằng năm. Nếu bản cũ đã gửi tin hôm nay, cài bản hằng năm sau 10:00 giờ Việt Nam để tránh gửi trùng trong ngày chuyển đổi.

## Chạy thử và xem nhật ký

```sh
# Xem trước mốc mở màn, giao thừa và mùng 1 ở các mùa khác nhau.
python3 bot.py --preview --date 2026-11-08
python3 bot.py --preview --date 2027-02-05
python3 bot.py --preview --date 2028-01-26

# Kiểm tra LaunchAgent đã đăng ký.
launchctl print "gui/$(id -u)/local.tet-countdown"

# Gửi một tin có nhãn “Tin nhắn thử” thật vào channel đã chọn.
python3 "$HOME/Library/Application Support/Tet Countdown/bot.py" --test-send

# Xem nhật ký sau khi LaunchAgent đã chạy.
tail -n 20 "$HOME/Library/Application Support/Tet Countdown"/{stdout,stderr}.log
```

Tin nhắn thử độc lập với lượt gửi hằng ngày. Trạng thái `not running` giữa các lượt chạy là bình thường. Nếu Slack trả HTTP 403 hoặc 404, kiểm tra webhook còn hoạt động và channel đã được cấp quyền. Để đổi webhook, chạy `./install.sh --replace-webhook` từ thư mục giải nén.

## Lịch gửi

LaunchAgent đánh thức script vào các phút 00, 15, 30 và 45 theo đồng hồ Mac. Script dùng `Asia/Ho_Chi_Minh` để chọn lượt 09:00 và chỉ gửi trong khung **09:00–09:59 giờ Việt Nam**. Lịch vẫn dùng giờ Việt Nam nếu bạn đổi múi giờ macOS. Bot ghi nhận ngày gửi sau khi Slack xác nhận để tránh gửi lại cùng ngày.

Để gửi đúng 09:00, máy cần đang bật, thức, có mạng và tài khoản cài bot đã đăng nhập. Bạn có thể đóng Terminal hoặc khóa màn hình. Nếu máy thức lại hoặc bạn đăng nhập trong khung 09:00–09:59, bot có thể gửi muộn trong khung đó. Qua 10:00, bot bỏ qua ngày đó. [Cơ chế lập lịch và sleep của launchd](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)

## Gỡ cài đặt

Từ thư mục đã giải nén, chạy `./uninstall.sh`. Lệnh dỡ LaunchAgent và xóa các tệp bot đã cài, bao gồm webhook cục bộ, trạng thái gửi và nhật ký. Bạn có thể xóa webhook trong trang quản trị Slack nếu muốn thu hồi URL.
