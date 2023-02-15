# Konwerter plików psq do csv
Zadaniem konwertera jest konwersja danych z plików `*.psq` do plików w formacie `*.csv` z danymi w formie binarnej.

Plik w formacie `*.psq` jest plikiem zawierającym informacje o przeprowadzonej rozgrywce w grze Gomoku. Format ten jest obecnie używany przez [Gomocup](https://gomocup.org/), czyli ogólnoświatowy turniej sztucznej inteligencji grającej w Gomoku i Renju. Pliki są obsługiwane przez menager Gomoku [Piskvork](https://github.com/plastovicka/Piskvork). 

W tym formacie można znaleźć następujące informacje dotyczące rozegranej partii:
- rozmiar planszy
- poziom przeciwników
- przeciwnik rozpoczynający partię
- współrzędne kolejnych ruchów przeciwników
- czas wykonywania ruchu
- nazwy przeciwników (tylko w rozgrywce turniejowej)
- kod błędu

## Przeznaczenie programu

Konwerter ten jest potrzeby w ramach pracy magisterskiej pt. *Program grający w kółko i krzyżyk wykorzystujący rachunek zdań* (ang. *Gomoku playing program using propositional calculus*).

## Struktura plików `*.csv`