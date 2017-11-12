import praw
import pdb
import random

SUBMISSION_ID = ""
SUBREDDIT = "tea"
NUM_WINNERS = 10


def main():
    reddit = authenticate()
    submission = reddit.submission(SUBMISSION_ID)
    comments = submission.comments.list()
    authors = set(c.author.name for c in comments)

    print(
        f"There are {len(authors)} unique authors of {len(comments)} comments in the thread:")
    print("\n".join(sorted(authors)))
    print()

    mods = set(m.name for m in reddit.subreddit(SUBREDDIT).moderator())
    authors = remove_mods(authors, mods)

    # TODO: Further disqualification / pruning criteria

    print(f"The folllowing {len(authors)} users remain qualified:")
    print("\n".join(sorted(authors)))
    print()

    winners = sorted(random.sample(authors, k=NUM_WINNERS))
    print(f"The {len(winners)} winners chosen are:")
    print("\n".join(winners))

    # sanity checks
    for winner in winners:
        assert(winner in authors)
        assert(winner not in mods)


def remove_mods(authors, mods):
    authors_minus_mods = authors - mods
    mods_removed = authors & mods
    print(
        f"There are now {len(authors_minus_mods)} authors after the following mods were removed:")
    print(f"\n".join(sorted(mods_removed)))
    print()
    return authors_minus_mods


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
