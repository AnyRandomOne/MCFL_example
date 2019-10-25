package com.sklcs.mainProject;

import com.github.javaparser.ast.stmt.*;

import java.util.Map;
import java.util.Set;

public class KeyVariableNameVisitor extends PredicateNameVisitor {
    @Override
    public void visit(final ReturnStmt returnStmt, Map<String, Set<String>> variableDict){
        //super.visit(returnStmt, variableDict);
        startPredicate(returnStmt);
        returnStmt.getExpression().ifPresent(l -> l.accept(this, variableDict));
        endPredicate();
        returnStmt.getComment().ifPresent(l -> l.accept(this, variableDict));
    }

    @Override
    public void visit(final ForEachStmt forEachStmt, Map<String, Set<String>> variableDict){
        //super.visit(forEachStmt, variableDict);
        forEachStmt.getBody().accept(this, variableDict);
        forEachStmt.getIterable().accept(this, variableDict);
        startPredicate(forEachStmt);
        forEachStmt.getVariable().accept(this, variableDict);
        endPredicate();
        forEachStmt.getComment().ifPresent(l -> l.accept(this, variableDict));
    }
}
