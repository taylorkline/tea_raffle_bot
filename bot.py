import praw
import pdb
import random
import datetime

SUBMISSION_ID = ""
NUM_WINNERS = 10
MIN_ACCOUNT_AGE_DAYS = 7
MIN_KARMA = 10
MIN_COMMENTS = 5


def main():
    reddit = authenticate()
    submission = reddit.submission(SUBMISSION_ID)
    comments = submission.comments.list()
    authors = set(c.author for c in comments)

    print(
        f"There are {len(authors)} unique authors of {len(comments)} comments in the thread:")
    print("\n".join(sorted((a.name for a in authors))))
    print()

    mods = set(m for m in submission.subreddit.moderator())
    disqualified = dict()
    choose_disqualified(authors, mods, disqualified)

    authors = authors - disqualified.keys()
    print(f"{len(authors)} authors remain qualified after the folllowing were removed:")
    for author, disqualification_reason in sorted(disqualified.items(), key=lambda x: x[0].name):
        print(f"{author.name} - {disqualification_reason}")
    print()

    print(f"The folllowing {len(authors)} users remain qualified:")
    print("\n".join(sorted(a.name for a in authors)))
    print()

    winners = random.sample(authors, k=NUM_WINNERS)
    print(f"The {len(winners)} winners chosen are:")
    print("\n".join(sorted(w.name for w in winners)))

    # sanity checks
    for winner in winners:
        assert(winner in authors)
        assert(winner not in mods)
        assert(winner not in disqualified)


def choose_disqualified(authors, mods, disqualified):
    now = datetime.date.today()
    for author in authors:
        # Prune mods
        if author in mods:
            disqualified[author] = "Is a moderator of the subreddit."
            continue

        # Prune accounts under min age
        account_created = datetime.date.fromtimestamp(author.created_utc)
        age = now - account_created
        assert(age.days >= 0)
        if age.days < MIN_ACCOUNT_AGE_DAYS:
            disqualified[author] = f"Account is only {age.days} old."
            continue

        # Prune accounts with low karma
        if author.comment_karma + author.link_karma < MIN_KARMA:
            disqualified[author] = f"Combined link and comment karma is {author.comment_karma + author.link_karma} versus cutoff of {MIN_KARMA}."
            continue

        # Prune accounts with fewer than the min number of comments
        comment_count = len(list(author.comments.new(limit=MIN_COMMENTS + 5))) + \
            len(list(author.submissions.new(limit=MIN_COMMENTS + 5)))
        if comment_count < MIN_COMMENTS:
            disqualified[author] = f"Author has only made {comment_count} versus the cutoff of {MIN_COMMENTS}."
            continue


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
