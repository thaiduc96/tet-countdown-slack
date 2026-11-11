# Bot Slack đếm ngược Tết 2027 trên macOS

Bot gửi tin mỗi ngày lúc **09:00 giờ Việt Nam**. Tin nhắn xen kẽ câu vui, lời động viên và chuyện ngày Tết, khoảng 40% số ngày có thêm liên kết tìm bài hát Tết trên YouTube. Ngày **05/02/2027** có tin giao thừa, ngày **06/02/2027** có lời chúc mùng 1. Từ ngày 07/02/2027 bot dừng gửi. [Lịch Tết 2027](https://baochinhphu.vn/nghi-tet-am-lich-2027-keo-dai-7-ngay-nghi-quoc-khanh-4-ngay-102261010095648278.htm)

## Cài đặt

1. Kiểm tra Python bằng `python3 --version`. Cần **Python 3.10 trở lên**. Nếu cần cài Python, tải bộ cài cho macOS, rồi mở lại Terminal. Bot dùng thư viện chuẩn Python và `curl` có sẵn trên macOS. [Tải Python cho macOS](https://www.python.org/downloads/macos/)
2. Nếu đã có Slack Incoming Webhook cho channel đích, dùng lại URL đó. Để tạo mới, mở Slack API → **Your Apps** → **Create New App** → **From scratch** → **Incoming Webhooks**. Bật **Activate Incoming Webhooks**, chọn **Add New Webhook to Workspace**, chọn channel rồi bấm **Allow**. Với channel riêng tư, tài khoản tạo webhook cần là thành viên của channel đó. Sao chép Webhook URL. [Hướng dẫn của Slack](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/)
3. Nếu lấy mã nguồn từ GitHub, dùng nút **Code** để sao chép lệnh hoặc URL clone, rồi mở Terminal trong thư mục vừa clone và chạy hai lệnh cuối bên dưới. Nếu dùng bản ZIP trong Downloads, chạy các lệnh sau.

   ```sh
   cd "$HOME/Downloads"
   unzip tet-countdown-slack-2027-macos.zip
   cd tet-countdown-slack-2027
   python3 bot.py --preview
   ./install.sh
   ```

   Dán Webhook URL tại lời nhắc trong Terminal và nhấn Enter. Terminal sẽ ẩn ký tự khi dán. Hãy chạy dưới tài khoản đang đăng nhập macOS. Bộ cài lưu webhook cục bộ với quyền `600`, trong thư mục `~/Library/Application Support/Tet Countdown 2027` có quyền `700`.

## Chạy thử và xem nhật ký

```sh
# Xem trước tin giao thừa hoặc mùng 1 ngay trong Terminal.
python3 bot.py --preview --date 2027-02-05
python3 bot.py --preview --date 2027-02-06

# Kiểm tra LaunchAgent đã đăng ký.
launchctl print "gui/$(id -u)/local.tet-countdown-2027"

# Gửi một tin có nhãn “Tin nhắn thử” thật vào channel đã chọn.
python3 "$HOME/Library/Application Support/Tet Countdown 2027/bot.py" --test-send

# Xem nhật ký sau khi LaunchAgent đã chạy.
tail -n 20 "$HOME/Library/Application Support/Tet Countdown 2027"/{stdout,stderr}.log
```

Tin nhắn thử độc lập với lượt gửi hằng ngày. Trạng thái `not running` giữa các lượt chạy là bình thường. Nếu Slack trả HTTP 403 hoặc 404, kiểm tra webhook còn hoạt động và channel đã được cấp quyền. Để đổi webhook, chạy `./install.sh --replace-webhook` từ thư mục giải nén.

## Lịch gửi

LaunchAgent đánh thức script vào các phút 00, 15, 30 và 45 theo đồng hồ Mac. Script dùng `Asia/Ho_Chi_Minh` để chọn lượt 09:00 và chỉ gửi trong khung **09:00–09:59 giờ Việt Nam**. Lịch vẫn dùng giờ Việt Nam nếu bạn đổi múi giờ macOS. Bot ghi nhận ngày gửi sau khi Slack xác nhận để tránh gửi lại cùng ngày.

Để gửi đúng 09:00, máy cần đang bật, thức, có mạng và tài khoản cài bot đã đăng nhập. Bạn có thể đóng Terminal hoặc khóa màn hình. Nếu máy thức lại hoặc bạn đăng nhập trong khung 09:00–09:59, bot có thể gửi muộn trong khung đó. Qua 10:00, bot bỏ qua ngày đó. [Cơ chế lập lịch và sleep của launchd](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)

## Gỡ cài đặt

Từ thư mục đã giải nén, chạy `./uninstall.sh`. Lệnh dỡ LaunchAgent và xóa các tệp bot đã cài, bao gồm webhook cục bộ, trạng thái gửi và nhật ký. Bạn có thể xóa webhook trong trang quản trị Slack nếu muốn thu hồi URL.
