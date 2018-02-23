## Use `git log` to see what's going on

`git log` shows a record of commits. You can add flags to make this a very insightful look at the various branches people are working on.

* `--oneline` compresses commit logs to oneline
* `--graph` visually shows various branches being created then merged back
* `--all` shows all commits, even on branches that don't interact with yours
* `--date=relative` makes the dates human-friendly (ie, "one week ago" and "just now")

So: `git log --oneline --graph --all --date=relative` will show something like this:

![git_log_screenshot](https://user-images.githubusercontent.com/16504363/32153624-bce46fea-bcf9-11e7-9215-39a07c8cec27.png)

Here, you can see:

* Each line represents a commit
* The alphanumeric string in yellow is a shortened version of the hash that uniquely identifies that commit.
* Commit `65bb805` is labeled as `origin/master`, because `origin`'s (aka GitHub's) version of the `master` branch  is pointing there. It is also labeled as `HEAD` because my own current, local 'view' of the code matches this commit. It is also labeled as `origin/HEAD` because GitHub's current view of the code (the one that shows up on the homepage of this project) matches this commit.
* If you look at the commit labeled `origin/db_structure` you can follow that green line down to see that Carolyn probably created this branch off of the commit titled `fb13447` (commit message: "FAIL"). Before she could push, she pulled the more recent of version of the code (follow the red branch back to `65bb805`, where my `dusty-refactor` was merged.)

## Delete local branches no longer on local

To delete local references to no longer existing remote branches:
1.  `git remote prune origin`

To delete local branches now merged into master:
1. `git checkout master`
2. `git branch --merged | grep -v '^[ *]*master$' | xargs git branch -d`

To delete local branches whose remote counterparts have been removed:
1. `git branch -vv | grep 'origin/.*: gone]' | awk '{print $1}' | xargs git branch -d`