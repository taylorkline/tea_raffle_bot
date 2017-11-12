import praw
import pdb
import random
import datetime

SUBMISSION_ID = ""
SUBREDDIT = "tea"
NUM_WINNERS = 10
MIN_ACCOUNT_AGE_DAYS = 7


def main():
    reddit = authenticate()
    submission = reddit.submission(SUBMISSION_ID)
    comments = submission.comments.list()
    authors = set(c.author for c in comments)

    print(
        f"There are {len(authors)} unique authors of {len(comments)} comments in the thread:")
    print("\n".join(sorted((a.name for a in authors))))
    print()

    mods = set(m for m in reddit.subreddit(SUBREDDIT).moderator())
    authors = remove_mods(authors, mods)

    authors = remove_new(authors)

    # TODO: Further disqualification / pruning criteria
    # Such as:
    # Combined comment + submission karma < 10
    # Number of submissions + comments < 10

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


def remove_mods(authors, mods):
    authors_minus_mods = authors - mods
    mods_removed = authors & mods
    print(
        f"There are now {len(authors_minus_mods)} authors after the following mods were removed:")
    print(f"\n".join(sorted((m.name for m in mods_removed))))
    print()
    return authors_minus_mods


def remove_new(authors):
    new_authors = set()
    for author in authors:
        now = datetime.date.today()
        account_created = datetime.date.fromtimestamp(author.created_utc)
        age = now - account_created
        assert(age.days >= 0)
        if age.days < MIN_ACCOUNT_AGE_DAYS:
            new_authors.add(author)
    authors_minus_new = authors - new_authors
    print(
        f"Removed {len(new_authors)} authors due to an account age < {MIN_ACCOUNT_AGE_DAYS} days:")
    print("\n".join(sorted(a.name for a in new_authors)))
    print()
    return authors_minus_new


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
