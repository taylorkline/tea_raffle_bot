import praw
import pdb
import random
import datetime

SUBMISSION_ID = "7foq2r"
PRIZES_TABLE_PATH = "prizes.md"

# for example, users who entered by accident
EXCLUDED_USERNAMES = set(["puerh_lover"])


def main():
    num_prizes = read_table(PRIZES_TABLE_PATH)
    assert(num_prizes > 0)
    print(f"{num_prizes} prizes are available.")

    reddit = authenticate()
    submission = reddit.submission(SUBMISSION_ID)
    comments = submission.comments.replace_more(
        limit=None)  # Retrieve every single comment
    # list(...) will give ONLY top-level comments. Intentional per contest rules.
    comments = list(submission.comments)
    excluded_authors = set(reddit.redditor(name)
                           for name in EXCLUDED_USERNAMES)
    authors = {c.author: c.body.replace(
        "\n", " ") for c in comments if c.author not in excluded_authors}

    print(
        f"There are {len(authors)} unique authors of {len(comments)} top-level comments in the thread.")

    mods = set(m for m in submission.subreddit.moderator())
    disqualified = dict()
    choose_disqualified(authors, mods, disqualified,
                        datetime.datetime.fromtimestamp(submission.created_utc), submission.subreddit)

    authors = {a: authors[a] for a in authors - disqualified.keys()}
    print(f"{len(authors)} authors remain qualified after the folllowing {len(disqualified)} authors were disqualified:")
    print("author|disqualification")
    print("------|----------------")
    for author, disqualification_reason in sorted(disqualified.items(), key=lambda x: x[0].name):
        print(f"/u/{author.name}|{disqualification_reason}")
    print()

    name_to_comment = {author.name: comment for author,
                       comment in authors.items()}
    winning_pool = random.sample(list(authors), k=num_prizes * 2)
    winners = winning_pool[:num_prizes]
    runner_ups = winning_pool[num_prizes:]
    assert(len(winners) == num_prizes)

    print(f"And the {len(winners)} winners are:")
    print("#|author|comment")
    print("-|------|-------")
    for rank, w in enumerate(winners):
        print(f"{rank + 1}|/u/{w.name}|{name_to_comment[w.name]}")
    del winners

    print(f"And the {len(runner_ups)} runner ups (for Reddit Gold and backups due to shipping restrictions, etc.) are:")
    print("#|author|comment")
    print("-|------|-------")
    for rank, ru in enumerate(runner_ups):
        print(f"{rank + 1}|/u/{ru.name}|{name_to_comment[ru.name]}")
    del runner_ups

    # sanity checks
    for winner in winning_pool:
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


def read_table(path):
    num_prizes = 0
    with open(path) as f:
        # discard header data
        f.readline()
        f.readline()

        for prizes_by_vendor in map(lambda line: int(line.split("|")[-1]), f.readlines()):
            num_prizes += prizes_by_vendor
    return num_prizes


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
