       IDENTIFICATION DIVISION.
       PROGRAM-ID. BANKING.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE  ASSIGN TO "input.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT ACC-FILE ASSIGN TO "accounts.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT TMP-FILE ASSIGN TO "temp.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT OUT-FILE ASSIGN TO "output.txt"
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.

       FD IN-FILE.
       01 IN-REC.
          05 IN-ACC-X       PIC X(6).
          05 IN-ACT         PIC X(3).
          05 IN-AMT-STR     PIC X(9).

       FD ACC-FILE.
       01 ACC-REC.
          05 ACC-ACC-X      PIC X(6).
          05 ACC-ACT        PIC X(3).
          05 ACC-AMT-STR    PIC X(9).

       FD TMP-FILE.
       01 TMP-REC.
          05 TMP-ACC-X      PIC X(6).
          05 TMP-ACT        PIC X(3).
          05 TMP-AMT-STR    PIC X(9).

       FD OUT-FILE.
       01 OUT-RECORD        PIC X(80).

       WORKING-STORAGE SECTION.
       77 IN-ACCOUNT         PIC 9(6).
       77 IN-ACTION          PIC X(3).
       77 IN-AMOUNT          PIC 9(7)V99.

       77 ACC-ACCOUNT        PIC 9(6).
       77 ACC-BALANCE        PIC 9(7)V99.

       77 TMP-BALANCE        PIC 9(7)V99.
       77 MATCH-FOUND        PIC X VALUE "N".
       77 UPDATED            PIC X VALUE "N".
       77 EOF-FLAG           PIC X VALUE "N".

       77 AMOUNT-EDITED      PIC 9(7).99.
       77 BALANCE-ALPHA      PIC X(15).

       77 RAI-TO-IDR-RATE    PIC 9(12) VALUE 120000000.
       77 BALANCE-IDR        PIC 9(15).
       77 BALANCE-IDR-ALPHA  PIC Z(12)9.
       77 PTR                PIC 9(4) VALUE 1.

       77 ARG-LINE           PIC X(80).
       77 INTEREST-RATE      PIC 9V999 VALUE 0.005.

       PROCEDURE DIVISION.

       MAIN.
           ACCEPT ARG-LINE FROM COMMAND-LINE
           IF ARG-LINE = "--apply-interest"
               PERFORM INTEREST-LOOP
               STOP RUN
           END-IF
           PERFORM NORMAL-MODE
           STOP RUN.

       NORMAL-MODE.
           PERFORM READ-INPUT
           PERFORM PROCESS-RECORDS
           IF MATCH-FOUND = "N"
               IF IN-ACTION = "NEW"
                   PERFORM APPEND-ACCOUNT
                   MOVE "ACCOUNT CREATED" TO OUT-RECORD
               ELSE
                   MOVE "ACCOUNT NOT FOUND" TO OUT-RECORD
               END-IF
           END-IF
           PERFORM FINALIZE.

       APPLY-INTEREST.
           OPEN INPUT ACC-FILE
           OPEN OUTPUT TMP-FILE
           MOVE "N" TO EOF-FLAG
           PERFORM UNTIL EOF-FLAG = "Y"
               READ ACC-FILE
                   AT END
                       MOVE "Y" TO EOF-FLAG
                   NOT AT END
                       MOVE FUNCTION NUMVAL(ACC-ACC-X)   TO ACC-ACCOUNT
                       MOVE FUNCTION NUMVAL(ACC-AMT-STR) TO ACC-BALANCE
                       COMPUTE TMP-BALANCE = ACC-BALANCE +
                           (ACC-BALANCE * INTEREST-RATE)
                       MOVE ACC-ACC-X     TO TMP-ACC-X
                       MOVE "BAL"         TO TMP-ACT
                       MOVE TMP-BALANCE   TO AMOUNT-EDITED
                       MOVE AMOUNT-EDITED TO TMP-AMT-STR
                       WRITE TMP-REC
                       DISPLAY "Applied interest to account "
                           ACC-ACCOUNT " new balance: " TMP-BALANCE
               END-READ
           END-PERFORM
           CLOSE ACC-FILE
           CLOSE TMP-FILE
           CALL "SYSTEM" USING "mv temp.txt accounts.txt".

       INTEREST-LOOP.
           PERFORM FOREVER
               PERFORM APPLY-INTEREST
               CALL "SYSTEM" USING "sleep 23"
           END-PERFORM.

       READ-INPUT.
           OPEN INPUT IN-FILE
           READ IN-FILE AT END
               DISPLAY "NO INPUT"
               STOP RUN
           END-READ
           CLOSE IN-FILE

           MOVE FUNCTION NUMVAL(IN-ACC-X)   TO IN-ACCOUNT
           MOVE IN-ACT                      TO IN-ACTION
           MOVE FUNCTION NUMVAL(IN-AMT-STR) TO IN-AMOUNT.

       PROCESS-RECORDS.
           OPEN INPUT ACC-FILE
           OPEN OUTPUT TMP-FILE
           MOVE "N" TO EOF-FLAG
           PERFORM UNTIL EOF-FLAG = "Y"
               READ ACC-FILE
                   AT END
                       MOVE "Y" TO EOF-FLAG
                   NOT AT END
                       MOVE FUNCTION NUMVAL(ACC-ACC-X)   TO ACC-ACCOUNT
                       MOVE FUNCTION NUMVAL(ACC-AMT-STR) TO ACC-BALANCE
                       IF ACC-ACCOUNT = IN-ACCOUNT
                           MOVE "Y" TO MATCH-FOUND
                           PERFORM APPLY-ACTION
                       ELSE
                           WRITE TMP-REC FROM ACC-REC
                       END-IF
               END-READ
           END-PERFORM
           CLOSE ACC-FILE
           CLOSE TMP-FILE.

       APPLY-ACTION.
           MOVE ACC-BALANCE TO TMP-BALANCE
           EVALUATE IN-ACTION
               WHEN "DEP"
                   ADD IN-AMOUNT TO TMP-BALANCE
                   MOVE "DEPOSITED MONEY" TO OUT-RECORD
               WHEN "WDR"
                   IF TMP-BALANCE >= IN-AMOUNT
                       SUBTRACT IN-AMOUNT FROM TMP-BALANCE
                       MOVE "WITHDREW MONEY" TO OUT-RECORD
                   ELSE
                       MOVE "INSUFFICIENT FUNDS" TO OUT-RECORD
                   END-IF
               WHEN "BAL"
                   MOVE SPACES TO OUT-RECORD
                   MOVE 1 TO PTR
                   MOVE TMP-BALANCE TO AMOUNT-EDITED
                   MOVE AMOUNT-EDITED TO BALANCE-ALPHA
                   STRING "BALANCE: "
                          BALANCE-ALPHA
                          DELIMITED SIZE
                          INTO OUT-RECORD
                          WITH POINTER PTR
                   MULTIPLY TMP-BALANCE BY RAI-TO-IDR-RATE
                       GIVING BALANCE-IDR
                   MOVE BALANCE-IDR TO BALANCE-IDR-ALPHA
                   STRING " | IDR: "
                          BALANCE-IDR-ALPHA
                          DELIMITED SIZE
                          INTO OUT-RECORD
                          WITH POINTER PTR
               WHEN OTHER
                   MOVE "UNKNOWN ACTION" TO OUT-RECORD
           END-EVALUATE

           MOVE IN-ACC-X     TO TMP-ACC-X
           MOVE IN-ACTION    TO TMP-ACT
           MOVE TMP-BALANCE  TO AMOUNT-EDITED
           MOVE AMOUNT-EDITED TO TMP-AMT-STR
           WRITE TMP-REC
           MOVE "Y" TO UPDATED.

       APPEND-ACCOUNT.
           OPEN EXTEND ACC-FILE
           MOVE IN-ACC-X     TO ACC-ACC-X
           MOVE "BAL"       TO ACC-ACT
           MOVE ZERO        TO AMOUNT-EDITED
           MOVE AMOUNT-EDITED TO ACC-AMT-STR
           WRITE ACC-REC
           CLOSE ACC-FILE.

       FINALIZE.
           IF UPDATED = "Y"
               CALL "SYSTEM" USING "mv temp.txt accounts.txt"
           END-IF
           OPEN OUTPUT OUT-FILE
           WRITE OUT-RECORD
           CLOSE OUT-FILE.
