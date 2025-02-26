import psycopg2

conpass='postgresql://bus_owner:npg_2GMITORHNJU5@ep-sweet-moon-a1j5r8v6-pooler.ap-southeast-1.aws.neon.tech/bus?sslmode=require'

#to test the connection to database
def connection_test():
    try:
        conn=psycopg2.connect(conpass)
        cur=conn.cursor()
        print("connection sucessful")
    except:
        print("connection failed")
    finally:
        cur.close()
        conn.close()

# Insert data into the 'bus' table
def insert_bus(bus_id, bus_start_location, bus_end_location):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "INSERT INTO bus (bus_id, bus_start_location, bus_end_location) VALUES (%s, %s, %s)"
        cur.execute(query, (bus_id, bus_start_location, bus_end_location))
        conn.commit()
    except Exception as e:
        print(f"Error inserting into bus table: {e}")
    finally:
        cur.close()
        conn.close()

# Insert data into the 'users' table
def insert_user(user_name, user_password, user_phone):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "INSERT INTO users (user_name, user_password, user_phone) VALUES (%s, %s, %s)"
        cur.execute(query, (user_name, user_password, user_phone))
        conn.commit()
    except Exception as e:
        print(f"Error inserting into users table: {e}")
    finally:
        cur.close()
        conn.close()

# Insert data into the 'bus_location' table
def insert_bus_location(bus_id, user_id, lon, lat):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        
        # Check if a record with the same bus_id already exists
        check_query = "SELECT 1 FROM bus_location WHERE bus_id = %s"
        cur.execute(check_query, (bus_id,))
        exists = cur.fetchone()
        
        if exists:
            # Update the existing record
            update_query = "UPDATE bus_location SET user_id = %s, bus_location = ST_GeographyFromText('SRID=4326;POINT(%s %s)'), updated_at = NOW() WHERE bus_id = %s"
            cur.execute(update_query, (user_id, lon, lat, bus_id))
        else:
            # Insert a new record
            insert_query = "INSERT INTO bus_location (bus_id, user_id, bus_location, updated_at) VALUES (%s, %s, ST_GeographyFromText('SRID=4326;POINT(%s %s)'), NOW())"
            cur.execute(insert_query, (bus_id, user_id, lon, lat))
        
        # Commit the transaction
        conn.commit()
    except Exception as e:
        print(f"Error inserting/updating bus_location table: {e}")
    finally:
        cur.close()
        conn.close()


# Insert data into the 'bus_stop' table
def insert_bus_stop(bus_stop_name, lon, lat, bus_stop_type):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "INSERT INTO bus_stop (bus_stop_name, bus_stop_location, bus_stop_type) VALUES (%s, ST_GeographyFromText('SRID=4326;POINT(%s %s)'), %s);"
        cur.execute(query, (bus_stop_name, lon, lat, bus_stop_type))
        conn.commit()
    except Exception as e:
        print(f"Error inserting into bus_stop table: {e}")
    finally:
        cur.close()
        conn.close()

# Insert data into the 'user_location' table
def insert_user_location(user_id, visited_location):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "INSERT INTO user_location (user_id, visited_location) VALUES (%s, %s)"
        cur.execute(query, (user_id, visited_location))
        conn.commit()
    except Exception as e:
        print(f"Error inserting into user_location table: {e}")
    finally:
        cur.close()
        conn.close()

# Get the last updated location of a bus 
def get_last_bus_location(bus_id):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "SELECT bus_id, ST_X(bus_location::geometry) AS longitude, ST_Y(bus_location::geometry) AS latitude FROM bus_location WHERE bus_id = %s ORDER BY updated_at DESC LIMIT 1;"
        cur.execute(query, (bus_id,))
        result = cur.fetchone()
        if result:
            bus_id, longitude, latitude = result
            print(f"Bus ID: {bus_id}, Longitude: {longitude}, Latitude: {latitude}")
            return (latitude,longitude)
        else:
            print("No location found for the specified bus ID.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

#get the closeset bus stop from your location
def get_closest_bus_stop(lon, lat):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "SELECT bus_stop_name, ST_X(bus_stop_location::geometry) AS longitude, ST_Y(bus_stop_location::geometry) AS latitude, ST_Distance(bus_stop_location, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) AS distance FROM bus_stop ORDER BY distance LIMIT 1;"
        cur.execute(query, (lon, lat))
        result = cur.fetchone()
        if result:
            return result
        else:
            print("No bus stops found.")
        
    except Exception as e:
        print(f"Error fetching closest bus stop: {e}")
    
    finally:
        cur.close()
        conn.close()

#delete all records related to a user
def delete_bus_location_by_user(user_id):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "DELETE FROM bus_location WHERE user_id = %s;"
        cur.execute(query, (user_id,))
        conn.commit()
        print(f"Records for user_id {user_id} deleted successfully.")
        
    except Exception as e:
        print(f"Error deleting records: {e}")
    
    finally:
        cur.close()
        conn.close()
        
def delete_bus_location_by_id(bus_id):
    try:
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        query = "DELETE FROM bus_location WHERE bus_id = %s;"
        cur.execute(query, (bus_id,))
        conn.commit()
        print(f"Records for bus_id {bus_id} deleted successfully.")
        
    except Exception as e:
        print(f"Error deleting records: {e}")
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close() 



#number of people currently in a bus
def get_user_count_in_bus(bus_id):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        
        # Query to count the number of users in the specified bus
        query = "SELECT COUNT(DISTINCT user_id) FROM bus_location WHERE bus_id = %s;"
        cur.execute(query, (bus_id,))
        
        # Fetch the result
        result = cur.fetchone()
        if result:
            print(f"Number of users in bus {bus_id}: {result[0]}")
        else:
            print(f"No users found for bus {bus_id}.")
        
    except Exception as e:
        # Handle any errors
        print(f"Error fetching user count: {e}")
    
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

# to check if user exists
def check_user_exists(user_name, user_password):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(conpass)
        cur = conn.cursor()
        
        # Query to count the number of users in the specified bus
        query = "SELECT user_id, user_name FROM users WHERE user_name = %s AND user_password = %s;"
        cur.execute(query, (user_name, user_password))
        
        # Fetch the result
        result = cur.fetchone()
        if result:
            return True
        else:
            return False
        
    except Exception as e:
        # Handle any errors
        print(f"Error fetching user : {e}")
    
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()    
        
        
# print(check_user_exists('a', '1234'))
# print(get_closest_bus_stop(76.409556,9.9635778))
# print(connection_test())
# insert_bus_location('BUS101', 1, 76.42007475535118,  9.971313713318702)