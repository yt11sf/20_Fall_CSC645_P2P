# P2P Decentralized Network with BitTorrent Protocol

Please use this README file to provide the following documentation for this project:

### Team Member:
1. Yee Jian Tan 920115752
2. Kevin Nunura 920347620
3. Brad Peraza 916768260
4. Peter Hu 917973828

### General Description:
* Handshake is established between peer.
* Communication protocol is in progress. 
* We have no success in transferring files.
* Communication Protocol:
  ```
  {
    'headers': 
    [
      {
        'type': 'print',
        'body': 
          {
            'message': 'Hello World'
          }
      },
      {
        'type': 'input',
        'body': 
          {
            'message': 'Enter Hello World',
            'res-key': 'Hello Response',
            'res-type': 'string'
          }
      },
      {
        'type': 'ignore'
      },
      {
        'type': 'bittorrent',
        'body': self.message.choke
      },
      {
        'type': 'close'
      }
    ]
  }
  ```

### How To Run:
1. In terminal, cd in to `P2P-Decentralized-Network`
2. In terminal, make sure the machine installed according to the requirements.txt
3. In `peer.py`, change the `SERVER_PORT` to 5000
4. In terminal, run `py peer.py`
5. In terminal, when prompted `Enter role: ` input `seeder`
6. In terminal, when prompted `Enter peer ip: ` just press `ENTER`
7. In terminal, when prompted `Start broadcast ` input `False`
8. In `peer.py`, change the `SERVER_PORT` to 4998
9. In 2nd terminal, run `py peer.py`
10. In 2nd terminal, when prompted `Enter role: ` input `peer`
11. In 2nd terminal, when prompted `Enter peer ip: ` just press `ENTER`
12. In 2nd terminal, when prompted `Start broadcast ` input `True`
### Challenges:
* Works have overlapped and caused confusion.
* Git is a nightmare for version controlling, and has forced us to abort many of our committs.
* One of our team members (Miguel) dropped the course unannounced mid project progress.
* One of our team members (YeeJian) was in a different time zone with a 12 hours difference which made setting up team
meets very challenging.
* We lost communication with Peter Hu on parts of the project.
* Everybody had problem understanding the tracker.py file.
* All team members are beginners with Python.
* Final labs prevented us from starting project sooner.
 
## Note that failure to provide the above docs will result in a 30% deduction in your final grade for this project. 

# Project Guidelines 

A document with detailed guidelines (P2P.pdf) to implement this project can be found in the 'help' folder and posted on iLearn

# The Tit-For-Tat Transfer Protocol

Your P2P program must implement the Tit-For-Tat transfer protocol. This protocol only allows a peer to be downloading/uploading
data from/to a maximum of four other peers or seeders; the top three with maximum upload rate, and a a random chosen peer. 
The goal of connecting to a random peer/seeder is to increment the participation of rarest peers in the network. This situation
must be reevaluated every 30 seconds because peers disconnect and connect all the time during the sharing process. 

See P2P.pdf for more info about how to compute temporal upload and downloads rates. 

# HTPBS for Showing Pieces Downloading/Uploading Progresses 

In order to show the progress of the pieces your peer is uploading or downloading to/from the P2P network, you can use the htpbs (horizontal threaded progress bars) library. This library tracks the progress of threaded jobs and is customizable to for your project. Exactly what you need for this project!. For more info about this library: https://pypi.org/project/htpbs/

### Install with PIP

```python 
pip3 install bencode.py
pip3 install torrent-parser
pip3 install bitarray
```

# Grading Rubric: 

1. This project is worth 25% of your final grade, and will be graded using a point scale where the 
maximum possible grade is 100 points. For example, a grade of 80/100 in this project will be converted to 
0.80 * 25% = 20% of 25%

2. The project has one extra-credit part: scaling the capability of the project to support sharing files in 
more than two swarms (5%). 

3. If the peer runs without errors, it connects to at least 2 peers that are already connected to the 
network, and you provided all the docs requested at the beginning of this README page then (+50)

4. If any of the requirements from step 3 is missing, I will apply a grade (at my discretion) depending on how much 
work the student has done in the project. However, this grade will be way below the 50 points threshold. 
Please make sure to test your project properly before submission to avoid this situation. 

5. For each part of the program that is correctly implemented (after step 3 is successfully executed), then (+10) points
Note that I will give also partial credit if there are parts that are not fully implemented but have some work done. 
Parts of the program are: (1) the torrent file is scanned correctly, (2) the tracker works as expected, (3) the 
Tit-for-Tac protocol implemented correctly (4) the blocks
and pieces are downloaded/uploaded/saved as expected and messages are correctly sent between peers, and
(5) real time progress of your program while downloading and uploading pieces is shown on screen. 

7. Late submissions won't be accepted since the due date for this project is set to the last day of class.

# Submission Guidelines 

This project is due the last day of the semester. After you complete and test your project, go to the assignments table, 
located in the main README file of this repository, and set this project to "done" or "completed". 
Failure to do that will result in your project not being graded because I will assume that the project 
hasn't been submitted. No exceptions here!!!. 

Good luck!!!
  

 


    


