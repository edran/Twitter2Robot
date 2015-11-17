import string
import json
import ConfigParser
import argparse
import tweepy


class Twitter2Robot(tweepy.StreamListener):

    valid = ['moveforward',
             'movebackward',
             'turnleft',
             'turnright',
             'kickleft',
             'kickright',
             'dance']

    def __init__(self, hashtag):
        self.hashtag = hashtag

    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)

        # Also, we convert UTF-8 to ASCII ignoring all bad characters
        # sent by users
        self.last_user = decoded['user']['screen_name']
        self.last_text = decoded['text'].encode('ascii', 'ignore')
        print '@%s: %s' % (self.last_user,
                           self.last_text)
        print "#######"
        self.parse_text()
        return True

    def on_error(self, status):
        print status

    def parse_text(self):
        try:
            hash = self.last_text.index(self.hashtag)
            # includes the space
            text = self.last_text[hash + len(self.hashtag):]
            text = text.replace(' ', '').lower()
            print self.validate_command(text)
        except ValueError:
            print "Could not parse message: %s" % text

    def validate_command(self, text):
        print "Raw command was: %s" % text
        while 1:
            if text[-1] not in string.ascii_lowercase:
                l = text[-1]
                text = text[:-1]
                print "Found some weird character at the end: %s" % l
            else:
                break
        print "Cleaned command: %s" % text
        return self.valid.index(text)


def read_config(path):
    cp = ConfigParser.ConfigParser()
    cp.read(path)
    ck = cp.get("CONSUMER", "key")
    cs = cp.get("CONSUMER", "secret")
    at = cp.get("ACCESS", "token")
    ase = cp.get("ACCESS", "secret")
    data = (ck, cs, at, ase)
    hashtag = cp.get("GENERAL", "hashtag")
    return data, hashtag


def parse_cmd():
    """
    Parses command line and returns path string.
    Expected `python -f input.txt`.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        dest='file',
                        required=True,
                        help='Path of file to analyse')
    args = parser.parse_args()
    return (args.file)


def main():
    path = parse_cmd()
    p, hashtag = read_config(path)
    consumer_key, consumer_secret, access_token, access_token_secret = p
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    ttr = Twitter2Robot(hashtag)
    print "Showing all new tweets for #" + hashtag + ":"
    stream = tweepy.Stream(auth, ttr)
    stream.filter(track=[hashtag])

if __name__ == "__main__":
    main()
