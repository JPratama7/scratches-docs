**Distributed Shorten URL Service**

## Requirements

### Functional requirements
- Given a long URL, the service should generate a shorter and unique alias for it (with maximum 6 characters).
- When the user hits a short link, the service should redirect to the original link.
- Links will expire after a standard default time span.

### Non-Functional requirements
- The system should be highly available. This is really important to consider because if the service goes down, all the URL redirection will start failing.
- URL redirection should happen in real-time with minimal latency.
- Shortened links should not be predictable.

## Capacity Planning

Assuming that service will be receive 30 million new request per month and  all links will be keep for 5 years.

### Data Modelling

this service will save this attributes for each short link:
- id (short link identifier)  [6 ascii characters]
- url (original url) [2000 ascii characters] [1] 
- created_at (unix timestamp) 
- expires_at (unix timestamp)

for each row we will use:
- 6 bytes (6 * 1 bytes) for id
- 2000 bytes (2000 * 1 bytes) for url
- 8 bytes (8 bytes) for created_at
- 8 bytes (8 bytes) for expires_at

with total = 2022 bytes for each short link

### Data Capacity Planning

With 30 million new request per month, annually we will have 360 million new request multiplied by 2022 bytes for each short link =  727920000000 bytes per year for storage per year = 3639600000000 bytes for 5 years which equal to 3.3101969166 TB (terabytes).


## Design 




Reference:
[1] https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers