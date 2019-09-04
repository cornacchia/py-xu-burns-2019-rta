* Genera un taskset di *n* task
  * Ogni task è HI-crit o LO-crit casualmente
  * Il rapporto tra HI e LO è fissato da un parametro *p*
  * I WCET dei task HI-crit sono controllati da un fattore *f* rispetto al loro LO-crit WCET
  * Le utilizzazioni (da cui si ricavano poi i WCET?) sono generate con UUnifast-discard
  * I periodi sono generati con log-uniform
    * Genera un vettore di valori uniformi tra logMin e logMax + Tg
    * Calcola e^ri (tutti i valori, si usa exp), divide per Tg e semplifica, poi moltiplica per Tg
    * [10, 1000] come range? 10 come granularità?
* Ordina i task in ogni taskset in ordine discendente per HI>LO e utilization
* Assegna i task ai processori con WorstFit ecc. (vedere XuBurns2015)
* Divide i task LO-crit in migratable e non migratable
* Crea le migration routes con il worst fit bin packing algorithm
* Response time analysis per il taskset secondo il modello 1, 2, 3, non migrating

I punti sopra vengono ripetuti per ogni taskset, non è specificato quanti siano (100?).

## Contributions:
Provare a utilizzare uno degli altri algoritmi come controprova (Randfixedsum)?
Uunifast-discard crea i taskset e elimina quelli che hanno un task con utilization > 1

Provare a considerare l'ipotesi che alcuni task LO-crit abbiano priorità maggiore di task HI-crit?

## Dubbi: 
1 - i task vanno inizialmente divisi usando Worst Fit Bin Packing?
2 - Forse aggiungere una spiegazione tipo quella di pag. 4
3 - Non è spiegato come dividere i LO-crit task in migratable o non migratable: vedere XuBurns2015 (cfr. pag. 3 MAIN paper)

