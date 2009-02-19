
class LeagueDao:
    def __init__(self, db):
        self.db = db

    def insertLeague(self, name, password):
        leagueId = self.db.insert('league', name=name, password=password)

        return leagueId

    def getLeagueById(self, id):
        leagues = self.db.select('league', where='id=$leagueId', vars={'leagueId':id})

        if len(leagues) > 0:
            return leagues[0]
        else:
            return None

    def getLeagueByName(self, name):
        leagues = self.db.select('league', where='name=$name', vars={'name':name})

        if (len(leagues) > 0):
            return leagues[0]
        else:
            return None

    def getPlayersByLeagueId(self, leagueId):
        players = self.db.select('player', where='league_id=$leagueId', vars={'leagueId':leagueId})

        return players

    def getLocationsByLeagueId(self, leagueId):
        locations = self.db.select('location', where='league_id=$leagueId', vars={'leagueId':leagueId})

        return locations

    def getGamesByLeagueId(self, leagueId):
        games = self.db.query('select g.* from game g, location l where l.league_id=$leagueId and l.id=g.location_id order by g.start_time asc', vars={'leagueId':leagueId})

        return games

class PlayerDao:
    def __init__(self, db):
        self.db = db

    def insertPlayer(self, leagueId, name):
        playerId = self.db.insert('player', league_id=leagueId, name=name)

        return playerId

class LocationDao:
    def __init__(self, db):
        self.db = db

    def insertLocation(self, leagueId, name):
        locationId = self.db.insert('location', league_id=leagueId, name=name)

        return locationId

    def getLocationById(self, locationId):
        locations = self.db.select('location', where='id=$locationId', vars={'locationId':locationId})

        if len(locations) > 0:
            return locations[0]
        else:
            return None

class GameDao:
    def __init__(self, db):
        self.db = db

    def insertGame(self, locationId):
        gameId = self.db.insert('game', location_id=locationId)

        return gameId

    def getGameById(self, gameId):
        games = self.db.select('game', where='id=$gameId', vars={'gameId': gameId})

        if len(games) > 0:
            return games[0]
        else:
            return None

    def addPlayerToGame(self, gameId, playerId):
        self.db.insert('game_players', game_id=gameId, player_id=playerId)

    def getPlayersInGame(self, gameId):
        players = self.db.query('select * from player where id in (select player_id from game_players where game_id=$gameId)', vars={'gameId': gameId})

        return players

    def insertGameScore(self, gameId):
        scoreId = self.db.insert('game_score', game_id=gameId)

        return scoreId

    def insertPlayerGameScore(self, gameScoreId, playerId, score):
        scoreId = self.db.insert('player_game_score', game_score_id=gameScoreId, player_id=playerId, score=score)

        return scoreId

    def getScoreByGameId(self, gameId):
        scores = self.db.query('select player_id, sum(score) as score, (select name from player where id=player_id) as player_name, (select l.name from location l, game g where g.id=$gameId and g.location_id=l.id) as location_name from player_game_score where game_score_id in (select id from game_score where game_id=$gameId) group by player_id order by score desc', vars={'gameId':gameId})

        return scores


