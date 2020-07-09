(defn getone [&rest body &kwonly [default None]]
  (try
    (get #*body)
    (except [_ [IndexError KeyError TypeError]]
      default)))



(defn c-not [var]
  (cond [(none? var) 0])
  (cond [(numeric? var)
         (cond [(zero? var) 0]
               [1])]))

(setv builtin-first first)
(defn first [arg]
  (builtin-first arg))


(defmain [&rest _]
  (print (getitem [0 [1 2] 3] 1 2 :default 0)))
