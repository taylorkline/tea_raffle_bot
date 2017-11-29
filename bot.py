import praw
import pdb
import random
import datetime

SUBMISSION_ID = ""
NUM_WINNERS = 10


def main():
    reddit = authenticate()
    submission = reddit.submission(SUBMISSION_ID)

    comments = submission.comments.replace_more(
        limit=None)  # Retrieve every single comment
    comments = submission.comments.list()
    authors = {c.author: c.body.replace("\n", " ") for c in comments}

    print(
        f"There are {len(authors)} unique authors of {len(comments)} comments in the thread.")

    mods = set(m for m in submission.subreddit.moderator())
    disqualified = dict()
    choose_disqualified(authors, mods, disqualified,
                        datetime.datetime.fromtimestamp(submission.created_utc), submission.subreddit)

    authors = {a: authors[a] for a in authors - disqualified.keys()}
    print(f"{len(authors)} authors remain qualified after the folllowing were removed:")
    print("author|disqualification")
    print("------|----------------")
    for author, disqualification_reason in sorted(disqualified.items(), key=lambda x: x[0].name):
        print(f"/u/{author.name}|{disqualification_reason}")
    print()

    name_to_comment = {author.name: comment for author,
                       comment in authors.items()}
    winners = random.sample(list(authors), k=NUM_WINNERS)
    print("author|comment")
    print("------|-------")
    for name in sorted(w.name for w in winners):
        print(f"/u/{name}|{name_to_comment[name]}")

    # sanity checks
    for winner in winners:
        assert(winner in authors)
        assert(winner not in mods)
        assert(winner not in disqualified)


def choose_disqualified(authors, mods, disqualified, contest_start, contest_subreddit):
    for author in sorted(authors, key=lambda a: a.name):
        print(f"Validating {author.name}... ", end="")

        # Prune mods
        if author in mods:
            disqualified[author] = "Is a moderator of the subreddit."
            print(f"disqualified: {disqualified[author]}")
            continue

        # Prune those without a comment or submission to the contest subreddit before contest date
        contributed_before_contest = False
        for comment in author.comments.new(limit=None):
            if (comment.subreddit == contest_subreddit and datetime.datetime.fromtimestamp(comment.created_utc) < contest_start):
                contributed_before_contest = True
                break

        if not contributed_before_contest:
            for submission in author.submissions.new(limit=None):
                if (submission.subreddit == contest_subreddit and datetime.datetime.fromtimestamp(submission.created_utc) < contest_start):
                    contributed_before_contest = True
                    break

        if not contributed_before_contest:
            disqualified[author] = "Did not make a comment or submission before contest date."
            print(f"disqualified: {disqualified[author]}")
            continue

        print("ok")


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
