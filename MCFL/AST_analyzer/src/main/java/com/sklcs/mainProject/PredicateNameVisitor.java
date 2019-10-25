package com.sklcs.mainProject;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.SimpleName;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.Map;
import java.util.Set;
import java.util.Stack;

public class PredicateNameVisitor extends NameVisitor {
    //private boolean inPredicate = false;
    private Stack<Node> predicateStack = new Stack<Node>();

    protected void startPredicate(Node node){
        //inPredicate = true;
        predicateStack.push(node);
    }

    protected void endPredicate(){
        //inPredicate = false;
        predicateStack.pop();
    }

    private boolean notInPredicate(){
        return predicateStack.empty();
    }

    @Override
    public void visit(final NameExpr nameExpr, Map<String, Set<String>> variableDict){
        if(notInPredicate()){
            return;
        }
//        String variableName = nameExpr.getName().toString();
//        String line =  packageName + "$" + fileName + ":" + startLine(searchStmt(nameExpr));
//        if(!variableDict.containsKey(line)){
//            variableDict.put(line, new HashSet<>());
//        }
//        variableDict.get(line).add(variableName);
        super.visit(nameExpr, variableDict);
    }

    @Override
    public void visit(final SimpleName simpleName, Map<String, Set<String>> variableDict){
        if(!notInPredicate()){
            super.visit(simpleName, variableDict);
        }
    }

    @Override
    public void visit(final IfStmt ifStmt, Map<String, Set<String>> variableDcit){
        startPredicate(ifStmt);
        ifStmt.getCondition().accept(this, variableDcit);
        endPredicate();
        ifStmt.getElseStmt().ifPresent(l -> l.accept(this, variableDcit));
        ifStmt.getThenStmt().accept(this, variableDcit);
        ifStmt.getComment().ifPresent(l -> l.accept(this, variableDcit));
    }

    @Override
    public void visit(final SwitchStmt switchStmt, Map<String, Set<String>> variableDcit){
        //super.visit(switchStmt, variableDcit);
        switchStmt.getEntries().forEach(p -> p.accept(this, variableDcit));
        startPredicate(switchStmt);
        switchStmt.getSelector().accept(this, variableDcit);
        endPredicate();
        switchStmt.getComment().ifPresent(l -> l.accept(this, variableDcit));
    }

    @Override
    public void visit(final SwitchEntry switchEntry, Map<String, Set<String>> variableDcit){
        //super.visit(switchEntry, variableDcit);
        startPredicate(switchEntry);
        switchEntry.getLabels().forEach(p -> p.accept(this, variableDcit));
        endPredicate();
        switchEntry.getStatements().forEach(p -> p.accept(this, variableDcit));
        switchEntry.getComment().ifPresent(l -> l.accept(this, variableDcit));
    }

    @Override
    public void visit(final WhileStmt whileStmt, Map<String, Set<String>> variableDict){
        //super.visit(whileStmt, variableDict);
        whileStmt.getBody().accept(this, variableDict);
        startPredicate(whileStmt);
        whileStmt.getCondition().accept(this, variableDict);
        endPredicate();
        whileStmt.getComment().ifPresent(l -> l.accept(this, variableDict));
    }

    @Override
    public void visit(final ForStmt forStmt, Map<String, Set<String>> variableDict){
        //super.visit(forStmt, variableDict);
        forStmt.getBody().accept(this, variableDict);
        startPredicate(forStmt);
        forStmt.getCompare().ifPresent(l -> l.accept(this, variableDict));
        endPredicate();
        forStmt.getInitialization().forEach(p -> p.accept(this, variableDict));
        forStmt.getUpdate().forEach(p -> p.accept(this, variableDict));
        forStmt.getComment().ifPresent(l -> l.accept(this, variableDict));
    }

    @Override
    public void visit(final DoStmt doStmt, Map<String, Set<String>> variableDict){
        //super.visit(doStmt, variableDict);
        doStmt.getBody().accept(this, variableDict);
        startPredicate(doStmt);
        doStmt.getCondition().accept(this, variableDict);
        endPredicate();
        doStmt.getComment().ifPresent(l -> l.accept(this, variableDict));
    }

    @Override
    public void visit(final ConditionalExpr conditionalExpr, Map<String, Set<String>> variableDict){
        //super.visit(conditionalExpr, variableDict);
        startPredicate(conditionalExpr);
        conditionalExpr.getCondition().accept(this, variableDict);
        endPredicate();
        conditionalExpr.getElseExpr().accept(this, variableDict);
        conditionalExpr.getThenExpr().accept(this, variableDict);
        conditionalExpr.getComment().ifPresent(l -> l.accept(this, variableDict));
    }
}
