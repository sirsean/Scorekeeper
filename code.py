#!/home/sirsean/local/bin/python
"""
Unfortunately, I haven't yet figured out how to make this line work normally on Dreamhost. I have to run a local version of Python, so in production this line has to be:
#!/home/sirsean/local/bin/python
But I'd really prefer it if it could always just be:
#!/usr/bin/env python
Make sure to switch to the former line any time we're in production.
"""

import web
import re
from datetime import datetime
from BasicDao import LeagueDao, PlayerDao, LocationDao, GameDao
import settings

db = web.database(
    dbn=settings.DATABASE_ENGINE, 
    host=settings.DATABASE_HOST, 
    db=settings.DATABASE_DB, 
    user=settings.DATABASE_USER, 
    pw=settings.DATABASE_PASSWORD)

leagueDao = LeagueDao(db)
playerDao = PlayerDao(db)
locationDao = LocationDao(db)
gameDao = GameDao(db)

# here we define template functions
def strftime(date, format):
    return datetime.strftime(date, format)
template_functions = {'strftime': strftime}

render = web.template.render('templates', base='layout', globals=template_functions)

urls = (
    '/game/(\d+)/enterScores/?', 'EnterScores',
    '/game/(\d+)/?', 'ViewGame',
    '/addLocation/?', 'AddLocation',
    '/addPlayer/?', 'AddPlayer',
    '/startGame/?', 'StartGame',
    '/league/add/?', 'CreateLeague',
    '/league/login/?', 'LoginToLeague',
    '/league/logout/?', 'LogoutFromLeague',
    '/league/?', 'ViewLeague',
    '/', 'home'
    )
app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'leagueId': 0})
    web.config._session = session
else:
    session = web.config._session

"""
I had a transaction interceptor installed that was working great, but the production environment, for some reason, throws an exception at the end of every request that triggers the rollback but otherwise everything executes correctly. So I had to remove this interceptor for it to work on Dreamhost. Damn it.
"""
def transaction_interceptor(handler):
    t = db.transaction()
    try:
        result = handler()
    except:
        t.rollback()
        raise
    else:
        t.commit()
    return result

def check_logged_in():
    if session.leagueId == 0:
        raise web.seeother('/')
    else:
        return session.leagueId

class CreateLeague:
    def GET(self):
        return render.createLeague()

    def POST(self):
        input = web.input()
        league = leagueDao.getLeagueByName(input.name)
        errors = []
        if league is not None:
            errors.append("That league already exists")
        if input.name is None or len(input.name) < 2:
            errors.append("The league name must be at least 2 characters")
        if input.password1 is None or len(input.password1) < 4:
            errors.append("The password must be at least 4 characters")
        if input.password1 != input.password2:
            errors.append("The passwords don't match")
        if len(errors) > 0:
            return render.createLeague(errors)
        id = leagueDao.insertLeague(input.name, input.password1)
        session.leagueId = id
        raise web.seeother('/league/')

class LoginToLeague:
    def GET(self):
        return render.login()

    def POST(self):
        input = web.input()
        league = leagueDao.getLeagueByName(input.name)
        errors = []
        if not league:
            errors.append("Login invalid")
        elif (league.password == input.password):
            session.leagueId = league.id
            raise web.seeother('/league/')
        else:
            errors.append("Login invalid")

        if len(errors) > 0:
            return render.login(errors)

class LogoutFromLeague:
    def GET(self):
        session.leagueId = 0
        raise web.seeother('/league/login/')

class AddLocation:
    def GET(self):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)

        return render.addLocation(league)

    def POST(self):
        leagueId = check_logged_in()
        input = web.input()

        errors = []
        if not input.name or len(input.name) < 2:
            errors.append("Location name must be at least 2 characters")
        
        if len(errors) > 0:
            league = leagueDao.getLeagueById(leagueId)
            return render.addLocation(league, errors)

        locationId = locationDao.insertLocation(leagueId, input.name)

        raise web.seeother('/league/')

class AddPlayer:
    def GET(self):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)

        return render.addPlayer(league)

    def POST(self):
        leagueId = check_logged_in()
        input = web.input()

        errors = []
        if not input.name or len(input.name) < 2:
            errors.append("Player name must be at least 2 characters")

        if len(errors) > 0:
            league = leagueDao.getLeagueById(leagueId)
            return render.addPlayer(league, errors)

        playerId = playerDao.insertPlayer(leagueId, input.name)

        raise web.seeother('/league/')

class StartGame:
    def GET(self):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)

        locations = leagueDao.getLocationsByLeagueId(leagueId)
        players = leagueDao.getPlayersByLeagueId(leagueId)

        return render.startGame(league, locations, players)

    def POST(self):
        leagueId = check_logged_in()
        input = web.input()
        locationId = input.locationId
        playerIds = []
        for key in input:
            if re.match('playerId_(\d+)', key):
                playerIds.append(re.match('playerId_(\d+)', key).group(1))

        gameId = gameDao.insertGame(locationId)
        for playerId in playerIds:
            gameDao.addPlayerToGame(gameId, playerId)

        raise web.seeother('/game/%s/' % gameId)

class EnterScores:
    def POST(self, gameId):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)
        game = gameDao.getGameById(gameId)

        input = web.input()

        scores = []
        for key in input:
            playerId = re.match('playerScore_(\d+)', key).group(1)
            scores.append((playerId, input[key]))

        gameScoreId = gameDao.insertGameScore(gameId)
        for (playerId, score) in scores:
            gameDao.insertPlayerGameScore(gameScoreId, playerId, score)

        raise web.seeother('/game/%s/' % gameId)

class ViewGame:
    def GET(self, gameId):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)
        game = gameDao.getGameById(gameId)
        location = locationDao.getLocationById(game.location_id)
        players = list(gameDao.getPlayersInGame(gameId))

        finalScores = []
        scores = db.select('game_score', where='game_id=$gameId', vars={'gameId':gameId}, order='start_time desc')
        for score in scores:
            playerScores = db.select('player_game_score', where='game_score_id=$gameScoreId', vars={'gameScoreId': score.id})
            finalScore = {}
            for player in players:
                finalScore[player.id] = 0
            for playerScore in playerScores:
                finalScore[playerScore.player_id] = playerScore.score
            finalScores.append(finalScore)

        totalScores = {}
        for player in players:
            totalScores[player.id] = 0
        for score in finalScores:
            for key in score:
                totalScores[key] += score[key]

        return render.viewGame(league, game, location, players, finalScores, totalScores)

class ViewLeague:
    def GET(self):
        leagueId = check_logged_in()
        league = leagueDao.getLeagueById(leagueId)

        locations = leagueDao.getLocationsByLeagueId(leagueId)
        players = leagueDao.getPlayersByLeagueId(leagueId)
        games = leagueDao.getGamesByLeagueId(leagueId)

        scores = []
        for game in games:
            scoreDict = {}
            scoreDict['game_id'] = game.id
            scoreDict['start_time'] = game.start_time
            scoreDict['location_name'] = game.location_name
            scoreDict['score'] = list(gameDao.getScoreByGameId(game.id))
            scores.append(scoreDict)

        return render.viewLeague(league, locations, players, scores)

class home:
    def GET(self):
        return render.index()

if __name__ == '__main__':
    app.run()
