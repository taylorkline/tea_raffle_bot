import praw
import pdb

SUBMISSION_ID = ""


def main():
    reddit = authenticate()
    pdb.set_trace()


def authenticate():
    return praw.Reddit("tearafflebot")


if __name__ == '__main__':
    main()
