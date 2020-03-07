# nypl-patron
Unofficial client for New York Public Library patrons

Example Usage:
``` python
user = NYPLPatron(123456790, 0000)
print(user.get_hold_info())
```

Output:
``` json
[
  {
    "title": "I never knew that about New York / Christopher Winn ; illustrations by Mai Osawa.",
    "status": "1 of 2 holds",
    "pickup location": "Mid-Manhattan Library at 42nd St",
    "cancel date": "11-11-20",
    "frozen": true
  },
  {
    "title": "Psychology of everyday things",
    "status": "8 of 27 holds",
    "pickup location": "Mid-Manhattan Library at 42nd St",
    "cancel date": "01-30-21",
    "frozen": false
  }
]
```

## Features  

* Get Hold Info
* Get Checkedout Info
* Get eBook Info

## Potential Enhanchments  

* Freeze Holds
* Renew Checkouts
* Get eBook holds