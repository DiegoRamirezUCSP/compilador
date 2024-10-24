Program → Declaration | Program Declaration

Declaration → Function | VarDecl

Function → Type Identifier ( Params ) { StmtList }

Type → IntType | BoolType | CharType | StringType | ArrayType | Void

ArrayType → Type [ ]

Params → Type Identifier | Type Identifier , Params | ε

VarDecl → Type Identifier ; | Type Identifier = Expression ;
StmtList → Statement | StmtList Statement
Statement → VarDecl | IfStmt | ForStmt | ReturnStmt | PrintStmt | ExprStmt | { StmtList }
IfStmt → if ( Expression ) Statement | if ( Expression ) Statement else Statement
ForStmt → for ( ExprStmt Expression ; ExprStmt ) Statement
ReturnStmt → return Expression ;
PrintStmt → print ( ExprList ) ;
ExprStmt → Expression ; | ;
ExprList → Expression | Expression , ExprList
Expression → Identifier = Expression | OrExpr | FunctionCall
FunctionCall → Identifier ( ExprList )
OrExpr → AndExpr | OrExpr || AndExpr
AndExpr → EqExpr | AndExpr && EqExpr
EqExpr → RelExpr | EqExpr == RelExpr | EqExpr != RelExpr
RelExpr → AddExpr | RelExpr < AddExpr | RelExpr > AddExpr | RelExpr <= AddExpr | RelExpr >= AddExpr
AddExpr → MulExpr | AddExpr + MulExpr | AddExpr - MulExpr
MulExpr → Unary | MulExpr * Unary | MulExpr / Unary | MulExpr % Unary
Unary → ! Unary | - Unary | Factor
Factor → Identifier | IntegerLiteral | CharLiteral | StringLiteral | BooleanLiteral | ArrayAccess | ( Expression )
ArrayAccess → Identifier [ Expression ]

