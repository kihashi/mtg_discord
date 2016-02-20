# -*- coding: utf-8 -*-
"""

Author:    John Cleaver <cleaver.john.k@gmail.com>
Copyright: 2016 John Cleaver
License:   BSD (See LICENSE file)
"""

import urllib
import sys
import discord
from modules import price as mtgprice
from modules import card as mtgcard

email = ""
password = ""

client = discord.Client()
client.login(email, password)

@client.event
def on_message(message):
    if message.content.startswith('.card'):
        reply = card(message.content[6:])
    elif message.content.startswith('.price'):
        reply = price(message.content[7:])
    elif message.content.startswith('.eprice'):
        reply = eprice(message.content[8:])
    elif message.content.startswith('.image'):
        reply = image(message.content[7:])
    elif message.content.startswith('.flavor'):
        reply = flavor(message.content[8:])
    elif message.content.startswith('.legality'):
        reply = legality(message.content[10:])
    elif message.content.startswith('.rulings'):
        reply = rulings(message.content[9:])
    else:
        reply = None

    if reply is not None:
        client.send_message(message.channel, u'@{USER}: {MESSAGE}'.format(USER=message.author, MESSAGE=reply))

@client.event
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def card(card_name):
    if card_name is not None and card_name != '':
        mtgcard.models.setup()
        try:
            card_text = mtgcard.find_card(card_name).get_card_text()
        except mtgcard.CardNotFoundError as e:
            card_text = (u"Could not find the card: {CARD}".format(CARD=unicode(e)))
        mtgcard.models.close()
        return card_text
    else:
        return u"Usage: '.card CARD_NAME'"


def price(card_name):
    if card_name != "":
        mtgcard.models.setup()
        try:
            card_name = mtgcard.find_card(card_name).name
        except mtgcard.CardNotFoundError as e:
            reply =  u"Could not find the card: {CARD}".format(CARD=unicode(e))
        else:
            reply = mtgprice.get_tcgplayer_price(card_name)
        mtgcard.models.close()
    else:
        reply = u"Usage: '.price CARD_NAME'"

    return reply


def eprice(card_name):
    if card_name != "":
        mtgcard.models.setup()
        try:
            card = mtgcard.find_card(card_name)
        except mtgcard.CardNotFoundError as e:
            reply = u"Could not find the card: {CARD}".format(CARD=unicode(e))
        else:
            reply = card.get_mtgoprice()
        mtgcard.models.close()
    else:
        reply = u"Usage: '.eprice CARD_NAME'"
    return reply


def legality(card_name):
    if card_name != "":
        mtgcard.models.setup()
        try:
            reply = mtgcard.find_card(card_name).get_legality()
        except mtgcard.CardNotFoundError as e:
            reply = u"Could not find the card: {CARD}".format(CARD=unicode(e))
        mtgcard.models.close()
    else:
        reply = u"Usage: '.legality CARD_NAME'"
    return reply


def rulings(card_name):
    if card_name != "":
        mtgcard.models.setup()
        input_text = card_name.split(u"|")
        card_name = input_text[0]
        if len(input_text) > 1:
            ruling_no = input_text[1]
            try:
                ruling_no = int(ruling_no)
            except ValueError:
                reply = u"That is is not a number. Try .ruling CardName | 1"
                return reply
        else:
            ruling_no = None
        try:
            card_rulings = mtgcard.find_card(card_name).get_rulings(ruling_no)
        except mtgcard.CardNotFoundError as e:
            reply = u"Could not find the card: {CARD}".format(CARD=unicode(e))
        else:
            reply = unicode(card_rulings[0]) + u" | " + unicode(card_rulings[1]) + u" of " + unicode(card_rulings[2])
        mtgcard.models.close()
    else:
        reply = u"Usage: '.rulings CARD_NAME [| RULING_NUMBER]'"
    return reply


def flavor(card_name):
    if card_name != "":
        mtgcard.models.setup()
        input_text = card_name.split("|")
        card_name = input_text[0]
        expansion_name = None
        if len(input_text) > 1:
            expansion_name = input_text[1].strip()
        try:
            card = mtgcard.find_card(card_name)
            if expansion_name is not None:
                expansion = mtgcard.find_expansion(expansion_name)
                release = mtgcard._find_release(card, expansion)
                reply = release.flavor_text
            else:
                reply = card.get_flavor_text()
        except mtgcard.CardNotFoundError as e:
            reply = u"Could not find the card: {CARD}".format(CARD=unicode(e))
        except mtgcard.ExpansionNotFoundError as e:
            reply = u"Could not find the expansion: {EXP}".format(EXP=unicode(e))
        except mtgcard.ReleaseNotFoundError as e:
            reply = u"That card is not in that set."
        mtgcard.models.close()
    else:
        reply = u"Usage: .flavor CARD_NAME [| SET_CODE]'"
    return reply


def image(card_name):
    if card_name != "":
        mtgcard.models.setup()
        input_text = card_name.split(u"|")
        card_name = unicode(input_text[0])
        expansion_name = None
        if len(input_text) > 1:
            expansion_name = unicode(input_text[1].strip())
        try:
            card = mtgcard.find_card(card_name)
            if expansion_name is not None:
                expansion = mtgcard.find_expansion(expansion_name)
                release = mtgcard._find_release(card, expansion)
                reply = quote(u"http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=" + unicode(release.multiverse_id) + u"&type=card", u":/,=&?")
            else:
                reply = quote(u"http://gatherer.wizards.com/Handlers/Image.ashx?name=" + card.name + u"&type=card", u":/,=&?'!Æt\"æÄäÁáÂâÖöÛûÜü")
        except mtgcard.CardNotFoundError as e:
            reply = u"Could not find the card: {CARD}".format(CARD=unicode(e))
        except mtgcard.ExpansionNotFoundError as e:
            reply = u"Could not find the expansion: {EXP}".format(EXP=unicode(e))
        except mtgcard.ReleaseNotFoundError as e:
            reply = u"That card is not in that set."
        mtgcard.models.close()
    else:
        reply = u"Usage: .image CARD_NAME [| SET_CODE]'"

    return reply


# from https://github.com/sopel-irc/sopel/blob/master/sopel/web.py
# Identical to urllib2.quote
def quote(string, safe='/'):
    """Like urllib2.quote but handles unicode properly."""
    if sys.version_info.major < 3:
        if isinstance(string, unicode):
            string = string.encode('utf8')
        string = urllib.quote(string, safe.encode('utf8'))
    else:
        string = urllib.parse.quote(str(string), safe)
    return string


client.run()
