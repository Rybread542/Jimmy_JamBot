# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 21:20:56 2023

@author: soycd
"""
import discord
from discord.ext import commands
import nest_asyncio
import spotify
import sql
from io import StringIO
import requests
from bs4 import BeautifulSoup as bs
import os
from dotenv import load_dotenv
import random

# Grabs bot token from locally stored file
load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

# Makes async events run without error. I really dont know
nest_asyncio.apply()



# runs bot w/ secret token        
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='-', intents=intents)
    

# prints to console when bot is online    
    @bot.event
    async def on_ready():
        print('go')

#  listens to all messages  
    @bot.listen('on_message')
    async def message_listen(message):
        if message.author == bot.user:
            return
        
#  prints every message sent by all users to the console. useful for debugging               
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        print(username, 'sent', user_message, 'in', channel)
        
        
        
################################commands######################################    

    
# simple radiohead test command        
    @bot.command()
    async def radiohead(ctx):
        await ctx.send('The greatest band on Earth. Radiohead rules. i love Thom Yorke. I want to marry Thom Yoke.')



# gets an album link and posts it 
# takes any number of arguments to deal with multi-word artists/titles       
    @bot.command()
    async def albumlink(ctx, *, arg):
        
        if ' - ' not in arg:
            # Attempts to retrieve a spotify link based on just the title. 
            # See spotify.py for details
            link = spotify.get_album_URL(arg, '')
            if link != 0:
                await ctx.send(link) 
                
            else:
                await ctx.send('Album not found! Try searching by "title - artist" if you haven\'t already.')   
        
        else:
            # Parse title and artist from arg
            title, artist = parse_title_artist(arg)
                
            # Retrieves link with title and artist
            link = spotify.get_album_URL(title, artist)
             
            # link will return 0 if Spotify API cannot return an accurate result. 
            # Bot will throw an error message in the chat if this happens
            if link != 0:
                await ctx.send(link)   
            else:
                await ctx.send('Album not found! Check your search and try again. Or maybe you\'re just unlucky.')      
                   

        
# Uses Spotify API to send a spotify link to the searched song
# Takes any number of args to deal with multi-word titles/artists            
    @bot.command()
    async def songlink(ctx, *, arg):
        
        # Parse title and artist from arg
        title, artist = parse_title_artist(arg)
        
        # Attempt to generate spotify URL. See spotify.py for details
        link = spotify.get_song_URL(title, artist)
        
        # Send link if one is found, throw error otherwise
        if link != 0:
            await ctx.send(link)   
        else:
            await ctx.send('Song not found! Check formatting and try again. This command accepts "Title - Artist"')
        
            

# Returns a random album from either the pool of a given member, or
# from the entire submitted album database.
# Takes the name of a member or "all" as an arg            
    @bot.command()
    async def randomalbum(ctx, arg=None):
        
        # Retrieves an album from the entire database if passed with
        # 'all' arg
        if arg == 'all' or arg == None:
            album = sql.get_random_album_from_db()
            
        # If a name is given, checks to make sure the name has a pool
        # else throws an error
        else:
            if arg in sql.pool_ids_nicknames:
                # Gets a random set of album data from the given pool in SQL. 
                # Returns as a list containing one tuple. 
                # See sql.py for details
                
                album = sql.get_random_album_from_pool(arg)
                      
            else:
                await ctx.send('That person doesn\'t have a pool!')
        
        # Grabs necessary album info from returned list.
        artist = album[0][0]
        title =  album[0][1]
        pool_id = album[0][2]
        
        
        # grabs name of the album pool taken from
        name = sql.get_pool_names_from_id(pool_id)
        
        
        # generates link from title/artist
        link = spotify.get_album_URL(title, artist)
        
        
        # sends link if successfully found, throws error if not and 
        # says name of attempted album for potential debugging purposes.
        if link != 0:
            await ctx.send(f'{link}\nfrom {name}\'s pool!')   
        else:
            await ctx.send(f'Album link not found! The album is {title} by {artist} from {name}\'s pool.')
    
    
    # Returns a .txt with moderately formatted data from the SQL server
    # shows given user's full album pool
    # can be called by any user to display the pool of any album club member
    @bot.command()
    async def albumpool(ctx, arg=None):
        
        # Checks to see if command is called with no name
        # Throws error if so
        if arg == None:
            await ctx.send('Who?')
        
        else:    
            # Checks name is in album club group
            # Else throws error
            if arg.lower() in sql.pool_ids_nicknames:
                
                # Grabs pool ID
                pool_id = sql.get_pool_id_from_name(arg)
                
                # Generates a list of tuples with album data
                pool = sql.get_pool(pool_id)
            
            else:
                await ctx.send("That person doesn't have a pool!")
                return
            
            # Initializes a string with album member's name for the title
            result = f'{arg}\'s album pool'
            
            # Iterates through the list of tuples, adding data to the
            # final string
            for i in range(len(pool)):
                
                # Each new tuple iteration adds two empty lines 
                # for better formatting 
                result += '\n \n'
                
                # Iterates through each tuple adding each piece of album
                # data to that row in the string followed by a bar for
                # formatting
                for j in range(len(pool[0])):
                    result += f'{pool[i][j]} | '
            
            # Prints the final, formatted data to a text file
            # and sends it 
            buffer = StringIO(result)
            f = discord.File(buffer, filename=f'{arg}_pool.txt')
            await ctx.send(file=f)

    
    # Adds a new album row to the SQL album database.
    # Will only add to ctx.user's pool, cannot be used to add an album 
    # to another pool and as such will only work when an active
    # member calls it
    @bot.command()
    async def addalbum(ctx, *, arg):
        
        # Calls pools from sql and generates user name string
        pools = sql.pool_ids_nicknames()
        user = str(ctx.author)
        
        # If user doesn't send a link, enforces title - artist format 
        if 'open.spotify.com/album/' not in arg:
            
            # Split title and artist from arg
            title, artist = parse_title_artist(arg)
            
            # Grabs link from title and artist
            link = spotify.get_album_URL(title, artist)
            
            # Throws error if Spotify can't find an accurate link
            if link == 0:
                await ctx.send('Failed to fetch album data. Check your formatting or get ' 
                                   'Rybread to enter it manually.')
                return
            
        
        # else spotify link is equal to passed arg
        else:
            link = arg  
            
        # checks user in pools, else throws error    
        if user in pools:
            
            # spotify.py uses link to generate relevant album data in a dict
            album = spotify.extract_album(link)
            
            # grabs pool id, adds it to album dict
            pool_id = sql.get_pool_id(pools[str(ctx.author)])
            album['pool_id'] = pool_id
            
            # checks album isn't already in the user's pool, else throws error
            if not sql.check_duplicate(album['title'], album['artist'], pool_id):
                
                # inserts album into user's pool, see sql.py for details
                # sends confirmation message
                sql.insert_album(album)
                await ctx.send(f"Successfully added {album['title']} by {album['artist']} to {user}\'s pool!")
                
            # else send error message
            else:
                await ctx.send('That album is already in your pool!')
        
        # error message if user is not in album club group
        else:
            await ctx.send('Seems you\'re not in the album club. You\'d better talk to RyBread!')
    
    
    # Removes an album from user's album pool
    @bot.command()
    async def removealbum(ctx, *, arg):
        # Set user
        user = str(ctx.author)
        
        
        # Make sure user is member of album club group
        if user in sql.pools():
            
            
            # Check if arg is spotify link
            if 'open.spotify.com/album/' not in arg:
                
                
                # Use parser if not a spotify link
                if ' - ' in arg:
                    title, artist = parse_title_artist(arg)
                else:
                    await ctx.send('Double check your formatting. I accept Spotify Links and "Title - Artist"')
                    
             
            # Grab title/artist from Spotify link
            else:
                album = spotify.extract_album(arg)
                title = album['title']
                artist = album['artist']
                
            
            # Get pool ID from user name
            pool_id = sql.get_pool_id_from_name(str(ctx.author))
            
            
            # Check to make sure album already exists in user's pool
            if sql.check_duplicate(title, artist, pool_id):
                
                
                # If album exists, remove it from user's pool and send confirmation
                sql.remove_album_from_pool(title, artist, pool_id)
                await ctx.send(f"Successfully removed {title} by {artist} from {user}\'s pool.")
                
             
            # Else throw error
            else:
                await ctx.send("That album isn't in your pool!")
        
        # Throw error if user outside album club group passes command
        else:
            await ctx.send('Seems you\'re not in the album club. You\'d better talk to RyBread!')
            
            
    # Runs the weekly album vote.
    # Requires confirmation from Rybread.
    # Grabs 4 random albums from a user's pool, sends them as Spotify links, and then sends
    # An embedded voting poll 
    # Rotates the order of album club members in SQL
    @bot.command()
    async def albumvote(ctx):
        
        # Rybread only command 
        if str(ctx.author) == 'ry.bread':
            
            # Set verification string for the vfcation embed message
            vfy = 'Run the next album vote? This will rotate the turn order.\n React to confirm.'
            
            # Run vfcation, does nothing if user denies
            if await verification_message(ctx, vfy):
                
                # Grabs the ID of the user next in the turn order
                next_id = sql.get_next_album_member()
                
                # Grabs user name for string printing
                name = sql.pool_names_from_id[next_id]
                
                # Initialize a list to store album links
                links = []
                
                # Initialize string for the poll embed
                # Initialize tuple of emojis for poll
                poll_desc = ''
                poll_emojis = ('1️⃣', '2️⃣', '3️⃣', '4️⃣')
                
                # Grabs a random album from the SQL database given the member's 
                # name. Sets artist and title from the album(list(tuple)) it returns
                while len(links) < 4:
                    album = sql.get_random_album_from_pool(name)
                    artist = album[0][0]
                    title = album[0][1]
                    
                    # Convert artist/title to a spotify link
                    link = spotify.get_album_URL(title, artist)
                    
                    # Prevents duplicate albums from being selected by checking 
                    # links already in the list
                    # Then adds the album to the list
                    if link not in links:
                        links.append(link)
                        
                        # Adds numbered emojis to the poll embed string
                        # followed by the title of each album
                        # as the links list fills with 4 links
                        poll_desc = poll_desc + f'{poll_emojis[len(links)-1]}' + ' ' + f'{title} \n\n'
                
                # Adds all links from links list to a string
                album_message = f"{links[0]}\n{links[1]}\n{links[2]}\n{links[3]}"
                
                # Adds data to a dictionary to be sent to create_embed
                poll_data = {'title': f'Vote from {name}\'s pool', 'description': poll_desc}
                poll = create_embed(poll_data)
                
                # Sends the 4 links to the channel followed by the poll embed
                # Then adds the voting reaction emojis to the embed
                await ctx.send(album_message)
                message = await ctx.send(embed=poll)
                for i in range(4):
                    await message.add_reaction(poll_emojis[i])
                
                # Finally, rotates the turn order of album members. 
                # See sql.py for details
                sql.decrement_album_members()
        
        # Else throw non rybread error
        else:
            await ctx.send('You are not my father. You cannot run the vote.')
            
    
    # Sets new album of the week
    # Updates AOTW channels 
    # deletes given album from SQL
    @bot.command()
    async def setaotw(ctx, *, arg):
        
        # rybread only command
        if str(ctx.author) == 'ry.bread':
            
            # Check for spotify link
            if 'open.spotify.com/album/' not in arg:
                
                 # If not spotify link, parse title/artist
                 # and convert to spotify link
                 title, artist = parse_title_artist(arg)
                 link = spotify.get_album_URL(title, artist)
                 
                 # Throw error if link not found
                 if link == 0:
                    await ctx.send('Failed to fetch album data. Check your formatting or get ' 
                                        'Rybread to enter it manually.')
                    return
            
            # Else set link to user input
            else:
                link = arg
            
            # Grab proper title artist from link
            album = spotify.extract_album(link)
            title = album['title']
            artist = album['artist']
            
            # Check album is in db
            if sql.is_in_db(title, artist):
                
                # Set string for vfcation embed
                vfy = 'Set album of the week? This will delete it from the pool.\n React to confirm.'
                
                # Send vfcation embed, proceeed if confirmed
                if await verification_message(ctx, vfy):
                    
                    # Remove given album from SQL database. See sql.py for details
                    sql.remove_album_from_db(title, artist)
                    
                    # Grab IDs of AOTW links channel and AOTW chat channel
                    aotw_link_channel = bot.get_channel(853776582903988235)
                    aotw_chat_channel = bot.get_channel(853776610736734218)
                    
                    # Send apotify link to AOTW links channel
                    await aotw_link_channel.send(link)
                    
                    # Edit AOTW chat channel to new album's title
                    await aotw_chat_channel.edit(name = title.lower())
                    
                    # Send confirmation
                    await ctx.send(f'Set album of the week to {title} by {artist}!')  
            
            
            # Throw error if album not in sql
            else:
                await ctx.send('That album isn\'t in the database!')
        
        # Throw error if not rybread
        else:
            await ctx.send("Yet another command that only Rybread is allowed to run. So sorry.")
                  
            
    # Pings Emeritus, Amanita and Rybread
    # Only works in jam-talk
    @bot.command()
    async def assemblejammers(ctx):
        
        # Check channel id
        if str(ctx.channel.id) == '854047567842508850':
            
            # Set name and send ping
            name = ctx.author
            await ctx.send(f'<@&1136465512151404575> {name} would like to jam!')
        
        # Throw error if not in jam-talk
        else:
            await ctx.send('Got to #jam-talk to use this command!')
    
    # Message listener
    # Listens for man carrying thing youtube videos
    # And posts an opinion poll
    @bot.listen('on_message')
    async def mct_listen(message):
        
        # Avoid looping by returning if message author is bot
        if message.author == bot.user:
            return
        
        # Convert message to string
        content = str(message.content)
        
        # Only look for youtube links
        if 'youtube.com/watch' in content or 'youtu.be/' in content:
            
            # scrape HTML from link and parse into HTML string
            page = requests.get(url = content)
            soup = bs(page.content, 'html.parser')
            
            # if MCT is author of the video, runs poll command
            if '"ownerChannelName":"Man Carrying Thing"' in str(soup):
                await dohemiss(message.channel)
            
                
    # Message listener
    # Listens for alien dance emojis
    # 33% chance to send a random alien danc emoji in response        
    @bot.listen('on_message')
    async def jam_listen(message):
        
        # avoid looping by returning if message author is bot
        if message.author == bot.user:
            return
        
        
        # Set message content to string
        content = str(message.content)
        
        # Initialize tuple of alienpls emotes
        emoji = ('<a:AlienPls:869563916332707841>', '<a:AlienPls3:869563871189434368>', 
                 '<a:AlienPls2:971830414916329512>', '<a:AlienPls4:971829525602250762>', 
                 '<a:AlienPls6:971838651858288710>', '<a:AlienPls5:971838345514737725>')
        
        # Compares each alienpls to the sent message
        # Allows for messages to have content besides the emote
        for i in range(len(emoji)):
            
            # If an alienpls is detected, rolls random int 1-3
            if emoji[i] in content:
                roll = random.randint(1, 3)
                
                # Sends random alienpls from tuple if rand rolls 2
                if roll == 2:
                    await message.channel.send(emoji[random.randint(0, 5)])
    
    
    # Creates and sends a verification message embed
    # using a given message string
    # Returns boolean based on emoji reaction from user
    async def verification_message(ctx, msg):
        
        # Gets and sends embed message with static title and description from passed string
        # Self-deletes after 45s of no input
        embed = create_embed({'title': 'Confirmation', 'description': msg})
        vfy_message = await ctx.send(embed=embed, delete_after = 45)
        
        # Initialize list of reaction emojis for yes and no
        votes = ['✅', '❌']
        
        # Add reactions to embed
        await vfy_message.add_reaction('✅')
        await vfy_message.add_reaction('❌')
        
        # Define check for reaction inputs. Still genuinely don't understand
        # how this works, but it does.
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in votes
        
        # Initializes bot listener for reaction emojis
        # The syntax here confuses me. But again, it works
        try:
            react, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
         
        # Print timeout error
        except nest_asyncio.asyncio.TimeoutError:
            print('timed out')
        
        # If a reaction is sent, delete verification embed
        # And return whether checkmark was selected
        else:
            await vfy_message.delete()
            return react.emoji == votes[0]
            
    
    # Create simple poll embed
    # For use with man carrying thing listener
    # Needs to be cleaned up
    @bot.command()
    async def dohemiss(ctx):
        poll= {}
        poll['title'] = "Do he miss?"
        poll['description'] = ":thumbsup:" + " "*2 + "no miss \n\n :thumbsdown:" + " "*2 + "he miss"
        embed = create_embed(poll)
        
        message = await ctx.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
    
    bot.run(TOKEN)

# Parser for commands that use album data inputs
# Takes a string with - delimiter and returns
# A title and an artist    
def parse_title_artist(string):
    separator = ' - '
    
    # Sets title to the substring before the delimiter
    title = string[0:string.index(separator)]
    
    # Sets artist to the remainder of the string after the delimiter
    artist = string[string.index(separator)+3:len(string)]
    
    return title, artist

# Create a simple embed message for use with various commands
# Takes a dictionary as an argument
def create_embed(fields):
    title = fields['title']
    description = fields['description']
    color = discord.Color.blue()
    embed = discord.Embed(title=title, description=description, color=color)
    
    return embed


    

