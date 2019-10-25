package com.sklcs.mainProject;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.expr.SimpleName;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.Stack;

public class NameVisitor  extends VoidVisitorAdapter<Map<String, Set<String>>> {
    protected String packageName;
    protected String fileName;

    private Stack<Node> simpleNameStack = new Stack<Node>();

    protected void startSimpleName(Node node){
        //inPredicate = true;
        simpleNameStack.push(node);
    }

    protected void endSimpleName(){
        //inPredicate = false;
        simpleNameStack.pop();
    }

    private boolean notInSimpleName(){
        return simpleNameStack.empty();
    }
    
    static String startLine(Node node) {
        if (node == null)
            return "-1";
        return Integer.toString(node.getRange().isPresent() ? node.getRange().get().startLine() : -1);
    }

    void setFileName(String fileName){
        String onlyName = fileName.split("\\.")[0];
        String[] fileList = onlyName.split("/");
        onlyName = fileList[fileList.length-1];
        this.fileName = onlyName;
        //System.out.println("file name : " + onlyName);
    }

    static String endLine(Node node) {
        if (node == null)
            return "-1";
        return Integer.toString(node.getRange().isPresent() ? node.getRange().get().endLine() : -1);
    }

    private static String searchClass(Node node){
        String className = "";
        Node nodeInSearch = node;
        while(nodeInSearch.getParentNode().isPresent()){
            nodeInSearch = nodeInSearch.getParentNode().get();
            if(nodeInSearch instanceof ClassOrInterfaceDeclaration){
                className = ((ClassOrInterfaceDeclaration) nodeInSearch).getName().toString();
                break;
            }
        }
        return className;
    }

    static Node searchStmt(Node node){
        Node nodeInSearch = node;
        while(nodeInSearch.getParentNode().isPresent()){
            nodeInSearch = nodeInSearch.getParentNode().get();
            if(nodeInSearch instanceof Statement){
                return nodeInSearch;
            }
        }
        return node;
    }

    @Override
    public void visit(CompilationUnit cu, Map<String, Set<String>> variableDict){
        packageName = "";
        if(cu.getPackageDeclaration().isPresent()){
            packageName = cu.getPackageDeclaration().get().getName().toString();
            //System.out.println("pakcageName: " + packageName);
        }
        super.visit(cu, variableDict);
    }

    @Override
    public void visit(final NameExpr nameExpr, Map<String, Set<String>> variableDict){
        String variableName = nameExpr.getName().toString();
        //String lineNo = startLine(nameExpr);
        //String methodName = searchMethod(nameExpr);
        //String className = searchClass(nameExpr);
        String line =  packageName + "$" + fileName + ":" + startLine(searchStmt(nameExpr));
        //System.out.println("line: " + line + " : " + variableName);
        if(!variableDict.containsKey(line)){
            variableDict.put(line, new HashSet<>());
        }
        variableDict.get(line).add(variableName);
    }

    @Override
    public void visit(final SimpleName simpleName, Map<String, Set<String>> variableDict){
        if(notInSimpleName()){
            return;
        }
        String name = simpleName.getIdentifier();
        String line =  packageName + "$" + fileName + ":" + startLine(searchStmt(simpleName));
        //System.out.println("line: " + line + " : " + variableName);
        if(!variableDict.containsKey(line)){
            variableDict.put(line, new HashSet<>());
        }
        variableDict.get(line).add(name);
    }

    @Override
    public void visit(final MethodCallExpr methodCallExpr, Map<String, Set<String>> variableDict){
//        String line =  packageName + "$" + fileName + ":" + startLine(searchStmt(methodCallExpr));
//        if(!variableDict.containsKey(line)){
//            variableDict.put(line, new HashSet<>());
//        }
//        variableDict.get(line).add(methodCallExpr.getName().getIdentifier());
        methodCallExpr.getArguments().forEach(p -> p.accept(this, variableDict));
        startSimpleName(methodCallExpr);
        methodCallExpr.getName().accept(this, variableDict);
        endSimpleName();
        methodCallExpr.getScope().ifPresent(l -> l.accept(this, variableDict));
        methodCallExpr.getTypeArguments().ifPresent(l -> l.forEach(v -> v.accept(this, variableDict)));
        methodCallExpr.getComment().ifPresent(l -> l.accept(this, variableDict));
    }

    @Override
    public void visit(final VariableDeclarator variableDeclarator, Map<String, Set<String>> variableDict){
//        String line =  packageName + "$" + fileName + ":" + startLine(searchStmt(variableDeclarator));
//        if(!variableDict.containsKey(line)){
//            variableDict.put(line, new HashSet<>());
//        }
//        variableDict.get(line).add(variableDeclarator.getName().getIdentifier());
//        super.visit(variableDeclarator, variableDict);
        variableDeclarator.getInitializer().ifPresent(l -> l.accept(this, variableDict));
        startSimpleName(variableDeclarator);
        variableDeclarator.getName().accept(this, variableDict);
        endSimpleName();
        variableDeclarator.getType().accept(this, variableDict);
        variableDeclarator.getComment().ifPresent(l -> l.accept(this, variableDict));
    }
}

