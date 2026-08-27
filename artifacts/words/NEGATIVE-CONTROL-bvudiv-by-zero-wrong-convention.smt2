(set-logic QF_BV)
; Negative control: claims bvudiv x 0 = 0, which is FALSE under SMT-LIB. Expected: sat (a counterexample exists).
(declare-const x (_ BitVec 8))
(assert (not (= (bvudiv x #x00) #x00)))
(check-sat)
