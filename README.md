# Tết Countdown for Slack

The bot posts in Vietnamese at **09:00 Vietnam time** each day from **90 days before Tết** through the first day of the Lunar New Year. The messages follow the season, from planning time off and booking tickets to shopping for new clothes, packing, and heading home. New Year's Eve and New Year's Day have their own messages. About 40% of countdown messages include a YouTube search link for a Tết song.

The bot reads `tet-dates.txt`, a table of Vietnamese Lunar New Year dates from **2026 through 2199**. The 2027 countdown begins on November 8, 2026, and the 2028 countdown begins on October 28, 2027. [Vietnamese lunar calendar data by Hồ Ngọc Đức](https://www.xemamlich.uhm.vn/JavaScript/)

## Create a Slack incoming webhook

1. Open **Slack Your Apps** and select **Create New App → From scratch**. Name the app and select your Slack workspace. [Slack Your Apps](https://api.slack.com/apps)
2. Open **Incoming Webhooks** and turn on **Activate Incoming Webhooks**.
3. Select **Add New Webhook to Workspace**, choose the channel, and click **Allow**. For a private channel, join it before adding the webhook. Copy the URL from **Webhook URLs for Your Workspace**. [Slack's incoming webhook guide](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/)

Store the webhook URL as a GitHub Actions secret or enter it at the macOS install prompt.

## Run on GitHub Actions

1. Use this repository or fork it into your own account. If you use a fork or rename the repository, update the full `OWNER/REPO` name in `jobs.countdown.if` in [.github/workflows/tet-countdown.yml](.github/workflows/tet-countdown.yml) on the default branch.
2. Go to **Settings → Secrets and variables → Actions → New repository secret**. Name it `SLACK_WEBHOOK_URL` and paste the Slack webhook URL into **Secret**. [GitHub's repository secret guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
3. Go to **Actions → Tết Countdown** and enable the workflow if prompted. Select **Run workflow** on the default branch and choose `preview` to see today's message in the log. Choose `send` to post today's countdown during an active countdown window.

If you use GitHub CLI, run the following command with your repository name. It prompts for the webhook URL.

```sh
gh secret set SLACK_WEBHOOK_URL --repo OWNER/REPO
```

When switching a channel from the macOS LaunchAgent to GitHub Actions, run `./uninstall.sh` on the Mac to avoid two deliveries on the same day.

GitHub schedules the workflow at 09:00 Vietnam time from October 23 through February 20. The bot checks the exact 90-day window before posting. GitHub may delay or skip scheduled runs during heavy load. Use `send` to catch up on the same day. The workflow saves a delivery marker after Slack confirms a post to help prevent duplicates. If the cache was cleared or a run failed after Slack accepted a message, check the channel before retrying. [GitHub's scheduling reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. Before the next countdown starts, check **Actions → Tết Countdown** and select **Enable workflow** if it was disabled. [GitHub's guide to enabling workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)

## Run on macOS

Check that `python3 --version` reports **Python 3.10 or later**. The bot uses the Python standard library and the `curl` included with macOS. [Download Python for macOS](https://www.python.org/downloads/macos/)

Open Terminal in the cloned or extracted `tet-countdown-slack` directory while signed in to macOS, then run the following commands.

```sh
python3 bot.py --preview
./install.sh
```

Paste the Slack webhook URL at the prompt and press Enter. Terminal hides the value as you enter it. The installer stores it locally in a file with mode `600` under `~/Library/Application Support/Tet Countdown`, which has mode `700`.

If you installed the original 2027-only version, have the webhook URL ready and run `./uninstall.sh` from the old version's source directory before installing this one. If the old version already posted today, install the annual version after 10:00 Vietnam time to avoid a duplicate during the changeover.

### Preview messages and inspect logs

```sh
# Preview the first countdown day, New Year's Eve, and New Year's Day.
python3 bot.py --preview --date 2026-11-08
python3 bot.py --preview --date 2027-02-05
python3 bot.py --preview --date 2028-01-26

# Check that the LaunchAgent is registered.
launchctl print "gui/$(id -u)/local.tet-countdown"

# Post a labeled test message to the configured Slack channel.
python3 "$HOME/Library/Application Support/Tet Countdown/bot.py" --test-send

# Inspect the logs after the LaunchAgent has run.
tail -n 20 "$HOME/Library/Application Support/Tet Countdown"/{stdout,stderr}.log
```

A test message is independent of the daily delivery. The LaunchAgent normally shows `not running` between runs. If Slack returns HTTP 403 or 404, check that the webhook is still active and authorized for the channel. To replace it, run `./install.sh --replace-webhook` from the source directory.

### How the macOS schedule works

The LaunchAgent starts the script at minutes 00, 15, 30, and 45 according to the Mac's clock. The script uses `Asia/Ho_Chi_Minh` to send at 09:00 Vietnam time, even if you change the Mac's time zone. It records the delivery date after Slack confirms the post.

For delivery at 09:00, keep the Mac awake and online with the installing user signed in. You can close Terminal or lock the screen. If the Mac wakes or you sign in between 09:00 and 09:59 Vietnam time, the bot may post later in that window. After 10:00, it skips that day's delivery. [Apple's guide to scheduling with launchd](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)

### Uninstall on macOS

Run `./uninstall.sh` from the source directory. It unloads the LaunchAgent and removes the installed files, including the local webhook, delivery state, and logs. You can revoke the webhook from the Slack app settings.
