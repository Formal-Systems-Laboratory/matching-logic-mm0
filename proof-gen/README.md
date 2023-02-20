```
spec DEFINEDNESS
    symbol def .
    metavars phi psi : Pattern .
    metavars X Y Z : SVar .
    metavars x y z : EVar .
    notation (ceil  phi) = (app (sym def) phi) .
    notation (floor phi) = (not (ceil (not phi))) .
    notation (equals phi psi) = (floor (iff phi psi))
endspec
```

becomes:

```metamathzero
imports "00-matching-logic.mm0"

term def : Symbol ;

--- Notation (ceil phi)
def (ceil phi) : Pattern = $ app (sym def) phi $ ;
theorem pos_in_ceil { X : SVar } (phi1 phi2 : Pattern X )
   (h1: $ _Positive X phi psi $)
 : $ _Positive X  $
 = '(...);
theorem push_eSubst_ceil ... ;
theorem apply_eSubst_ceil {X : EVar } (psi phi1 rho1 : Pattern X)
   (h1: $ Norm s[ psi / X ] phi1 $)
 :      $ Norm s[ psi / X ] (ceil phi1)$
 = (apply_eSubst_app apply_eSubst_disjoint h1) ;


def (floor phi) : Pattern = $ app (syn def) phi $ ;
```
