-- Add sample movies to the database
-- Run this after creating a user and making them admin

USE movie_db;

-- Sample movies (you'll need to replace uploaded_by with actual user ID)
INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by) VALUES
('The Shawshank Redemption', 'Movie', 'Drama', 1994, 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'Tim Robbins, Morgan Freeman, Bob Gunton', 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg', 'https://www.youtube.com/watch?v=6hB3S9bIaco', 1),
('The Godfather', 'Movie', 'Crime, Drama', 1972, 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.', 'Marlon Brando, Al Pacino, James Caan', 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg', 'https://www.youtube.com/watch?v=sY1S34973zA', 1),
('Pulp Fiction', 'Movie', 'Crime, Drama', 1994, 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.', 'John Travolta, Uma Thurman, Samuel L. Jackson', 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg', 'https://www.youtube.com/watch?v=s7EdQ4FqbhY', 1),
('The Dark Knight', 'Movie', 'Action, Crime, Drama', 2008, 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.', 'Christian Bale, Heath Ledger, Aaron Eckhart', 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg', 'https://www.youtube.com/watch?v=EXeTwQWrcwY', 1),
('Fight Club', 'Movie', 'Drama', 1999, 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.', 'Brad Pitt, Edward Norton, Helena Bonham Carter', 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg', 'https://www.youtube.com/watch?v=SUXWAEX2jlg', 1); 