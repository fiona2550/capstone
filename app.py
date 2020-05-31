from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS
from models import setup_db, Actors, Movies
#from auth import AuthError, requires_auth

COUNT_PER_PAGE = 10

def paginate_results(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * COUNT_PER_PAGE
        end = start + COUNT_PER_PAGE        
        results = [result.format() for result in selection]
        current_results = results[start:end]
        return current_results 

def create_app(test_config=None):
        # Create and configure the app
        app = Flask(__name__)
        setup_db(app)
        db_drop_and_create_all()
        CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

        @app.after_request
        def after_request(response):
                response.headers.add(
                        'Access-Control-Allow-Headers', 
                        'Content-Type,Authorization')
                response.headers.add(
                        'Access-Control-Allow-Methods', 
                        'GET,PUT,POST,DELETE,OPTIONS')
                return response
                
        '''
        ----1 GET----
        @TODO: 
        Create an endpoint to handle GET requests 
        for all available movies.
        '''
        
        @app.route('/actors', methods=['GET'])
        #@requires_auth('get:actors')
        def get_actors(jwt):
                try:
                        return jsonify({
                                'success': True,
                                'actors': paginate_results(request, Actor.query.all())
                        })
                except:
                        abort(422)

        #        GET Movies
        #        ----------------------------------------------------------------
        @app.route('/movies', methods=['GET'])
        #@requires_auth('get:movies')
        def get_movies(jwt):
                try:
                        return jsonify({
                        'success': True,
                        'movies': paginate_results(request, Movie.query.all())
                        })
                except:
                        abort(422)

        '''
        ----3 POST----
        @TODO: 
        Create an endpoint to handle POST requests 
        for all available actors and movies.
        '''
        
        @app.route('/actors', methods=['POST'])
        #@requires_auth('post:actors')
        def create_actor(jwt):
                body = request.json
                if not body:
                        abort(400)
                name = body.get('name', None)
                age = body.get('age', None)
                gender = body.get('gender', None)

                if (not name) or (not age) or (not gender):
                        abort(422)

                # Create and insert a new actor
                new_actor = Actors(name=name, age=age, gender=gender)
                new_actor.insert()

                # Return the newly created actor
                return jsonify({
                        'success': True,
                        'created': new_actor.actor_id
                })

        #        POST Movies
        #        ----------------------------------------------------------------
        @app.route('/movies', methods=['POST'])
        #@requires_auth('post:movies')
        def create_movie(jwt):
                body = request.json
                if not body:
                        abort(400)
                title = body.get('title', None)
                release_date = body.get('release_date', None)

                if not title or not release_date:
                        abort(422)

                # Create and insert a new movie
                new_movie = Movies(title=title, release_date=release_date)
                new_movie.insert()

                # Return the newly created movie
                return jsonify({
                        'success': True,
                        'created': new_movie.movie_id
                })

        '''
        ----4 DELETE----
        @TODO: 
        Create an endpoint to handle DELETE requests 
        for all available actors and movies.
        '''
        @app.route('/actors/<int:actor_id>', methods=['DELETE'])
        #@requires_auth('delete:actors')
        def delete_actor(jwt, actor_id):
                if not actor_id:
                        abort(400)

                actor_to_delete = Actor.query.get(actor_id)
                actor_to_delete.delete()

                return jsonify({
                        'success': True,
                        'deleted': actor_id
                })

        @app.route('/movies/<int:movie_id>', methods=['DELETE'])
        #@requires_auth('delete:movies')
        def delete_movie(jwt, movie_id):
                if not movie_id:
                        abort(400)
                movie_to_delete = Movie.query.get(movie_id)
                movie_to_delete.delete()

                return jsonify({
                        'success': True,
                        'deleted': movie_id
                })

        '''
        ----5 PATCH----
        @TODO: 
        Create an endpoint to handle PATCH requests 
        for all available actors and movies.
        '''
        
        @app.route('/actors/<int:actor_id>', methods=['PATCH'])
        #@requires_auth('patch:actors')
        def patch_actor(jwt, actor_id):
                if not actor_id:
                        abort(400)
                actor_to_patch = Actor.query.get(actor_id)
                if not actor_to_patch:
                        abort(404)

                body = request.json
                new_name = body.get('name', None)
                new_age = body.get('age', None)
                new_gender = body.get('gender', None)

                # Update the actor with the requested fields
                actor_to_patch.name = new_name
                actor_to_patch.age = new_age
                actor_to_patch.gender = new_gender
                actor_to_patch.update()

                # Return the updated actor
                return jsonify({
                        'success': True,
                        'edited': actor_to_patch.actor_id,
                        'actors': [Actor.query.get(actor_id).format()]
                })


        @app.route('/movies/<int:movie_id>', methods=['PATCH'])
        #@requires_auth('patch:movies')
        def update_movie(jwt, movie_id):
                if not movie_id:
                        abort(400)
                movie_to_patch = Movie.query.get(movie_id)
                if not movie_to_patch:
                        abort(400)

                body = request.json
                new_title = body.get('title', None)
                new_release_date = body.get('release_date', None)

                # Update the movie with the requested fields
                movie_to_patch.title = new_title
                movie_to_patch.release_date = new_release_date
                movie_to_patch.update()

                # Return the updated movie
                return jsonify({
                        'success': True,
                        'edited': movie_to_patch.movie_id,
                        'movies': [Movie.query.get(movie_id).format()]
                })

        '''
        ----Error Handlers----
        '''
        
        @app.errorhandler(422)
        def unprocessable(error):
                return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "Unprocessable."
                }), 422


        @app.errorhandler(404)
        def not_found_error(error):
                return jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "Resource not found."
                }), 404

        @app.errorhandler(400)
        def bad_request(error):
                return jsonify({
                        "success": False, 
                        "error": 400,
                        "message": str(error)
                }), 400
        '''
        @app.errorhandler(AuthError)
        def auth_error(auth_error):
                return jsonify({
                        "success": False,
                        "error": auth_error.status_code,
                        "message": auth_error.error['description']
                }), auth_error.status_code
        '''
        return app

app = create_app()

if __name__ == '__main__':
        app.run()