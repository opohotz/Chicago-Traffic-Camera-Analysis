# header comment! Overview, name, etc.
#
import sqlite3
import matplotlib.pyplot as plt

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    # Query and plot number of cameras per intersection
    dbCursor.execute("""
        SELECT Intersections.Intersection, COUNT(RedCameras.Camera_ID)
        FROM RedCameras
        JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
        GROUP BY Intersections.Intersection_ID
        ORDER BY COUNT(RedCameras.Camera_ID) DESC;
    """)
    camera_results = dbCursor.fetchall()

    if camera_results:
        intersections = [row[0] for row in camera_results]
        camera_counts = [row[1] for row in camera_results]

        # Create a bar chart for the number of cameras per intersection
        plt.figure(figsize=(10, 6))
        plt.bar(intersections, camera_counts, color='skyblue')
        plt.title("Number of Red Light Cameras at Each Intersection")
        plt.xlabel("Intersection")
        plt.ylabel("Number of Cameras")
        plt.xticks(rotation=90)  # Rotate intersection names for readability
        plt.tight_layout()
        plt.show()

    
##################################################################  
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Chicago Traffic Camera Analysis")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

print("Select a menu option: ")
print("  1. Find an intersection by name")
print("  2. Find all cameras at an intersection")
print("  3. Percentage of violations for a specific date")
print("  4. Number of cameras at each intersection")
print("  5. Number of violations at each intersection, given a year")
print("  6. Number of violations by year, given a camera ID")
print("  7. Number of violations by month, given a camera ID and year")
print("  8. Compare the number of red light and speed violations, given a year")
print("  9. Find cameras located on a street")
print("or x to exit the program.")

#Take in prompt from user
val = input("Enter your option: ").strip().lower()
if val == "x":
        print("Exiting program.")
        exit(0)

dbCursor = dbConn.cursor()
match val:
    case "1":
        # INTERSECTION
        user_input = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")

        sql = """
            SELECT
                Intersections.Intersection_ID,
                Intersections.Intersection,
                COUNT(SpeedCameras.Camera_ID) AS num_speed_cameras
            FROM
                SpeedCameras
            JOIN
                Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
            WHERE
                Intersections.Intersection LIKE ?
            GROUP BY
                Intersections.Intersection_ID
            ORDER BY
                num_speed_cameras DESC, Intersections.Intersection_ID ASC;
        """
        dbCursor.execute(sql, (user_input + "%",))
        result = dbCursor.fetchall()

        if not result:
            print("No intersections found matching your input.")
        else:
                print("\nResults:")
                print("ID   | Intersection Name")
                print("------------------------")
                for row in result:
                    print(f"{row[0]:<4} | {row[1]}")
                print()  # Blank line for readability

    case "2":
        user_input = input("Enter the name of the intersection (no wildcards allowed): ")

        # Query for Red Light Cameras
        sql_red = """
        SELECT RedCameras.Camera_ID, RedCameras.Address
        FROM RedCameras
        JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
        WHERE Intersections.Intersection = ?
        ORDER BY RedCameras.Camera_ID ASC;
        """

        # Query for Speed Cameras
        sql_speed = """
        SELECT SpeedCameras.Camera_ID, SpeedCameras.Address
        FROM SpeedCameras
        JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
        WHERE Intersections.Intersection = ?
        ORDER BY SpeedCameras.Camera_ID ASC;
        """

        dbCursor.execute(sql_red, (user_input,))
        red_cameras = dbCursor.fetchall()

        dbCursor.execute(sql_speed, (user_input,))
        speed_cameras = dbCursor.fetchall()

        if not red_cameras and not speed_cameras:
            print("No red light cameras found at that intersection.")
            print("No speed cameras found at that intersection.")
        else:
            if red_cameras:
                print("\nRed Light Cameras:")
                for cam in red_cameras:
                    print(f" {cam[0]} : {cam[1]}")
            else:
                print("\nNo red light cameras found at that intersection.")

            if speed_cameras:
                print("\nSpeed Cameras:")
                for cam in speed_cameras:
                    print(f" {cam[0]} : {cam[1]}")
            else:
                print("\nNo speed cameras found at that intersection.")

        print()  # Blank line for readability
    case "3":
        user_date = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ").strip()

        # Query to get the number of red light violations for the given date
        sql_red = """
        SELECT COUNT(*) FROM RedViolations WHERE Violation_Date = ?;
        """

        # Query to get the number of speed violations for the given date
        sql_speed = """
        SELECT COUNT(*) FROM SpeedViolations WHERE Violation_Date = ?;
        """

        dbCursor.execute(sql_red, (user_date,))
        red_count = dbCursor.fetchone()[0]

        dbCursor.execute(sql_speed, (user_date,))
        speed_count = dbCursor.fetchone()[0]

        total_violations = red_count + speed_count

        if total_violations == 0:
            print("No violations on record for that date.")
        else:
            red_percent = (red_count / total_violations) * 100
            speed_percent = (speed_count / total_violations) * 100

            print("\nNumber of Red Light Violations:", f"{red_count:,}", f"({red_percent:.3f}%)")
            print("Number of Speed Violations:", f"{speed_count:,}", f"({speed_percent:.3f}%)")
            print("Total Number of Violations:", f"{total_violations:,}")

        print()

    case "4":
        dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
        total_red = dbCursor.fetchone()[0]

        dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
        total_speed = dbCursor.fetchone()[0]

        # Get number of red light cameras per intersection
        sql_red_per_intersection = """
        SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(RedCameras.Camera_ID)
        FROM RedCameras
        JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
        GROUP BY Intersections.Intersection_ID
        ORDER BY COUNT(RedCameras.Camera_ID) DESC;
        """
        dbCursor.execute(sql_red_per_intersection)
        red_results = dbCursor.fetchall()

        # Get number of speed cameras per intersection
        sql_speed_per_intersection = """
        SELECT Intersections.Intersection_ID, Intersections.Intersection, COUNT(SpeedCameras.Camera_ID)
        FROM SpeedCameras
        JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
        GROUP BY Intersections.Intersection_ID
        ORDER BY COUNT(SpeedCameras.Camera_ID) DESC;
        """
        dbCursor.execute(sql_speed_per_intersection)
        speed_results = dbCursor.fetchall()

        # Display Red Light Camera Data
        print("\nNumber of Red Light Cameras at Each Intersection")
        for intersection_id, name, count in red_results:
            percentage = (count / total_red) * 100 if total_red > 0 else 0
            print(f" {name} ({intersection_id}) : {count} ({percentage:.3f}%)")

        # Display Speed Camera Data
        print("\nNumber of Speed Cameras at Each Intersection")
        for intersection_id, name, count in speed_results:
            percentage = (count / total_speed) * 100 if total_speed > 0 else 0
            print(f" {name} ({intersection_id}) : {count} ({percentage:.3f}%)")

        print()

    case "5":
        user_year = input("Enter the year (YYYY) to look for violations: ").strip()
      

        sql_red = """
            SELECT Intersections.Intersection, COUNT(RedViolations.[Correct_Violation_Column])
            FROM RedViolations
            JOIN RedCameras ON RedViolations.Camera_ID = RedCameras.Camera_ID
            JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
            WHERE strftime('%Y', Violation_Date) = ?
            GROUP BY Intersections.Intersection_ID;
            """

        dbCursor.execute(sql_red, (user_year,))
        red_results = dbCursor.fetchall()

        sql_speed = """
        SELECT Intersections.Intersection, COUNT(SpeedViolations.Violation_ID)
        FROM SpeedViolations
        JOIN SpeedCameras ON SpeedViolations.Camera_ID = SpeedCameras.Camera_ID
        JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Intersections.Intersection_ID;
        """
        dbCursor.execute(sql_speed, (user_year,))
        speed_results = dbCursor.fetchall()

        print(f"\nViolations at Intersections in {user_year}:")
        print("Intersection | Red Violations | Speed Violations")
        print("-----------------------------------------------")
        for red_row, speed_row in zip(red_results, speed_results):
            print(f"{red_row[0]}: {red_row[1]} Red, {speed_row[1]} Speed")

        print()

    case "6":
        user_camera_id = input("Enter the camera ID to get violations per year: ").strip()

        sql = """
        SELECT strftime('%Y', Violation_Date), COUNT(*) FROM RedViolations
        WHERE Camera_ID = ?
        GROUP BY strftime('%Y', Violation_Date)
        """
        dbCursor.execute(sql, (user_camera_id,))
        red_results = dbCursor.fetchall()

        sql = """
        SELECT strftime('%Y', Violation_Date), COUNT(*) FROM SpeedViolations
        WHERE Camera_ID = ?
        GROUP BY strftime('%Y', Violation_Date)
        """
        dbCursor.execute(sql, (user_camera_id,))
        speed_results = dbCursor.fetchall()

        print(f"\nViolations for Camera {user_camera_id}:")
        print("Year | Red Violations | Speed Violations")
        print("-----------------------------------------")
        for red_row, speed_row in zip(red_results, speed_results):
            print(f"{red_row[0]}: {red_row[1]} Red, {speed_row[1]} Speed")

        print()
        

    case "7":
        user_camera_id = input("Enter the camera ID and year (YYYY) to get violations per month: ").strip()
        user_year = input("Enter the year (YYYY): ").strip()

        sql_red = """
        SELECT strftime('%m', Violation_Date), COUNT(*) FROM RedViolations
        WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
        GROUP BY strftime('%m', Violation_Date)
        """
        dbCursor.execute(sql_red, (user_camera_id, user_year))
        red_results = dbCursor.fetchall()

        sql = """
         SELECT strftime('%m', Violation_Date), COUNT(*) FROM SpeedViolations
        WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
        GROUP BY strftime('%m', Violation_Date)
        """
        dbCursor.execute(sql, (user_camera_id, user_year))
        speed_results = dbCursor.fetchall()

        print(f"\nViolations for Camera {user_camera_id} in {user_year}:")
        print("Month | Red Violations | Speed Violations")
        print("-----------------------------------------")
        for red_row, speed_row in zip(red_results, speed_results):
            print(f"{red_row[0]}: {red_row[1]} Red, {speed_row[1]} Speed")

        # Extract month and count values for plotting
        months = [row[0] for row in red_results]
        red_violations = [row[1] for row in red_results]
        speed_violations = [row[1] for row in speed_results]

        # Create line plots for violations by month
        plt.figure(figsize=(10, 6))
        plt.plot(months, red_violations, marker='o', label="Red Violations", color='red')
        plt.plot(months, speed_violations, marker='o', label="Speed Violations", color='blue')
        plt.title(f"Monthly Violations for Camera {user_camera_id} in {user_year}")
        plt.xlabel("Month")
        plt.ylabel("Number of Violations")
        plt.xticks(months)  # Show month numbers on the x-axis
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        print()

         
    case "8":
        user_year = input("Enter the year (YYYY) to compare red light and speed violations: ").strip()
        sql_red = """
            SELECT COUNT(*) FROM RedViolations WHERE strftime('%Y', Violation_Date) = ?
            """
        dbCursor.execute(sql_red, (user_year,))
        red_count = dbCursor.fetchone()[0]

        sql_speed = """
            SELECT COUNT(*) FROM SpeedViolations WHERE strftime('%Y', Violation_Date) = ?
            """
        dbCursor.execute(sql_speed, (user_year,))
        speed_count = dbCursor.fetchone()[0]

        print(f"\nViolations Comparison for {user_year}:")
        print(f"Red Light Violations: {red_count}")
        print(f"Speed Violations: {speed_count}")

        # Create a bar chart to compare red light and speed violations
        plt.figure(figsize=(6, 4))
        labels = ['Red Light Violations', 'Speed Violations']
        counts = [red_count, speed_count]

        plt.bar(labels, counts, color=['red', 'blue'])
        plt.title(f"Red Light vs. Speed Violations in {user_year}")
        plt.ylabel("Number of Violations")
        plt.show()

        print()


    case "9":
        user_street = input("Enter the street name to find cameras: ").strip()

        sql_red = """
        SELECT RedCameras.Camera_ID, RedCameras.Address
        FROM RedCameras
        WHERE RedCameras.Address LIKE ?
        """
        dbCursor.execute(sql_red, ('%' + user_street + '%',))
        red_cameras = dbCursor.fetchall()

        sql_speed = """
        SELECT SpeedCameras.Camera_ID, SpeedCameras.Address
        FROM SpeedCameras
        WHERE SpeedCameras.Address LIKE ?
        """
        dbCursor.execute(sql_speed, ('%' + user_street + '%',))
        speed_cameras = dbCursor.fetchall()

        print("\nCameras on Street:", user_street)
        if not red_cameras and not speed_cameras:
            print("No cameras found on this street.")
        else:
            if red_cameras:
                print("\nRed Light Cameras:")
                for cam in red_cameras:
                    print(f" {cam[0]} : {cam[1]}")
            if speed_cameras:
                print("\nSpeed Cameras:")
                for cam in speed_cameras:
                    print(f" {cam[0]} : {cam[1]}")

        print()

    case _:
        print("Invalid option. Please try again.")

        



print("Exiting program.")
dbConn.close()
#
# done

#
