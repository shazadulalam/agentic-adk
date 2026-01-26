# Offline Push Behavior

## Overview

The git push daemon has been updated to **handle offline scenarios gracefully**. It will **NOT attempt to push when offline**, and will instead:

1. ✅ **Detect offline status** before attempting push
2. ✅ **Save commits locally** (commits are created even if push fails)
3. ✅ **Retry automatically** when back online (up to 3 retries)
4. ✅ **Log all attempts** for monitoring

## How It Works

### Online Detection

The daemon checks connectivity in two ways:
1. **Network connectivity**: Tests if `github.com` is reachable
2. **Git remote accessibility**: Tests if the git remote is accessible

Only if **both checks pass** will it attempt to push.

### Retry Logic

- **Max retries**: 3 attempts
- **Retry delay**: 5 minutes between retries
- **Behavior**: If offline, waits 5 minutes and retries (up to 3 times)

### Commit Safety

**Important**: Commits are created **locally** even if the push fails. This means:
- ✅ Your work is saved locally
- ✅ You can push manually when back online: `git push origin main`
- ✅ No data loss if push fails

## Behavior Scenarios

### Scenario 1: Online at Scheduled Time
```
[12:00] Scheduled push time
[12:00] ✓ Online detected
[12:00] ✓ Push successful
[12:00] ✓ Daemon completes
```

### Scenario 2: Offline at Scheduled Time
```
[12:00] Scheduled push time
[12:00] ⚠ Offline detected
[12:00] ✓ Commit created locally (saved)
[12:00] ⚠ Will retry in 5 minutes
[12:05] ⚠ Still offline, retry 1/3
[12:10] ⚠ Still offline, retry 2/3
[12:15] ⚠ Still offline, retry 3/3
[12:15] ✗ Max retries reached
[12:15] ℹ Commits saved locally - push manually when online
```

### Scenario 3: Offline, Then Comes Online
```
[12:00] Scheduled push time
[12:00] ⚠ Offline detected
[12:00] ✓ Commit created locally
[12:05] ⚠ Still offline, retry 1/3
[12:10] ✓ Online detected!
[12:10] ✓ Push successful
[12:10] ✓ Daemon completes
```

## Manual Push (When Back Online)

If the automatic push failed due to being offline, you can push manually:

```bash
# Check if there are unpushed commits
git log origin/main..HEAD

# Push manually
git push origin main

# Or use the push scripts directly
bash DataAgent/.git_auto_push_1.sh
bash DataAgent/.git_auto_push_2.sh
```

## Monitoring

### Check Daemon Status
```bash
ps aux | grep git_push_daemon
```

### View Push Logs
```bash
cat DataAgent/.git_auto_push.log
```

### Check for Unpushed Commits
```bash
git log origin/main..HEAD --oneline
```

## Configuration

You can adjust retry behavior in `.git_push_daemon.py`:

```python
MAX_RETRIES = 3              # Maximum retry attempts
RETRY_DELAY_MINUTES = 5      # Minutes between retries
```

## Benefits

1. **No Failed Pushes**: Won't attempt push when offline
2. **Data Safety**: Commits saved locally even if push fails
3. **Automatic Recovery**: Retries when back online
4. **Clear Logging**: All attempts logged for monitoring
5. **Manual Option**: Can push manually when convenient

## Important Notes

- ⚠️ **Commits are created locally** even if push fails
- ⚠️ **No data loss** - your work is always saved
- ✅ **Automatic retry** when back online (within retry window)
- ✅ **Manual push available** if automatic retries exhausted
- ✅ **All actions logged** for transparency

---

**Answer to your question**: 

**No, the code will NOT be pushed automatically when you're offline.** 

The daemon will:
1. Detect that you're offline
2. Create commits locally (saving your work)
3. Retry when you come back online (up to 3 times)
4. If all retries fail, log the failure and save commits locally

You can always push manually when back online using `git push origin main`.
