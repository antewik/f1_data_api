# f1_info_api

f1_info_api is a Python Flask Web API that provides Formula 1 race and standings information.  
It communicates with the [FastF1](https://github.com/theOehrly/Fast-F1) library (and Ergast via FastF1) to fetch live and historical F1 data, and exposes it through simple REST endpoints.  
This API is consumed by my ASP.NET Core portfolio web app (AvikstromPortfolio).

---

## Features
- **Next Race Endpoint** – Get details of the upcoming F1 race, including sessions with local and UTC times.  
- **Driver Standings Endpoint** – Current driver standings with points, wins, constructor, and nationality.  
- **Team Standings Endpoint** – Current constructor standings with points, wins, and team details.  
- **Ping Endpoint** – Simple health check for API availability.  
- **Swagger UI** – Interactive API documentation at `/apidocs`.  

---

