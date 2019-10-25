package com.sklcs.mainProject;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.BodyDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.Stack;

public class TestCaseSplitParser extends AbstractParser {
    TestCaseSplitParser(String resultFile) throws IOException {
        super(resultFile, new String[]{}, 2);
    }

    @Override
    public void parse(String filePath){
        try{
            //System.out.println(filePath);
            this.writer.setFileNow(filePath);
            FileInputStream fileInputStream = new FileInputStream(filePath);
            //StaticJavaParser.getConfiguration().setLanguageLevel(JAVA_1_4);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            //cu.accept(new AddBordersParser.BorderVisitor(), this.writer);
            //System.out.println(cu.toString());
            cu.accept(new SplitVisitor(), this.writer);
            fileInputStream.close();
            FileOutputStream fileOutputStream = new FileOutputStream(filePath);
            fileOutputStream.write(cu.toString().getBytes());
        }
        catch (Exception e){
            System.out.println("exception: " + e);
        }
    }

    public class InspectVisitor extends VoidVisitorAdapter<ParserWriter> {
        private Set<String> assertFunctionSet;
        private Set<String> testFunctionSet;
        private boolean hasAssert;

        @Override
        public void visit(final CompilationUnit cu, ParserWriter parserWriter){
            int assertNumbers, testNumbers;
            assertFunctionSet = new HashSet<>();
            testFunctionSet = new HashSet<>();
            do {
                assertNumbers = assertFunctionSet.size();
                testNumbers = testFunctionSet.size();
                super.visit(cu, parserWriter);
                //System.out.println("assert: " + assertNumbers + "->" + assertFunctionSet.size());
                //System.out.println("test: " + testNumbers + "->" + testFunctionSet.size());
            }while( assertFunctionSet.size() != assertNumbers
                    && testFunctionSet.size() != testNumbers);
        }

//        private boolean isAssertCall(MethodCallExpr methodCallExpr){
//            String callName = methodCallExpr.getName().toString();
//            return callName.indexOf("assert") == 0 ||
//                    callName.equals("fail") ||
//                    assertFunctionSet.contains(callName);
//        }
        @Override
        public void visit(final MethodCallExpr methodCallExpr, ParserWriter parserWriter){
            String callName = methodCallExpr.getNameAsString();
            if(!assertFunctionSet.contains(callName)){
                if(callName.indexOf("assert") == 0 ||
                        //callName.equals("fail") ||
                        //this is obviously false!
                        //assertFunctionSet.contains(callName))
                        callName.equals("fail"))
                    assertFunctionSet.add(callName);
            }
            if(assertFunctionSet.contains(callName)){
                hasAssert = true;
            }
            super.visit(methodCallExpr, parserWriter);
        }

        @Override
        public void visit(final MethodDeclaration methodDeclaration, ParserWriter parserWriter){
            String methodName = methodDeclaration.getNameAsString();
            hasAssert = false;
            super.visit(methodDeclaration, parserWriter);
            if(hasAssert){
                if(methodDeclaration.getParameters().size() == 0 &&
                        methodDeclaration.getNameAsString().indexOf("test") == 0) {
                    testFunctionSet.add(methodName);
                } else{
                    assertFunctionSet.add(methodName);
                }
            }
        }

        Set<String> getTestFunctionSet(){
            return testFunctionSet;
        }

        Set<String> getAssertFunctionSet(){
            return assertFunctionSet;
        }
    }

    public class RemoveVisitor extends ModifierVisitor<ParserWriter> {
        private Set<String> testFunctionSet;
        private boolean meetTestFunc;

        @Override
        public Visitable visit(final ExpressionStmt expressionStmt, ParserWriter parserWriter){
            meetTestFunc = false;
            //expressionStmt.accept(this, parserWriter);
            super.visit(expressionStmt, parserWriter);
            if(meetTestFunc) {
                return null;
            }
            else{
                return expressionStmt;
            }
        }

        @Override
        public Visitable visit(final MethodCallExpr methodCallExpr, ParserWriter parserWriter){
            //System.out.println("call: " + methodCallExpr.getName().toString());
            //if(methodCallExpr.getParentNode().isPresent())
            //    System.out.println("father node: " + methodCallExpr.getParentNode().get().getClass());
            if(testFunctionSet.contains(methodCallExpr.getNameAsString()) &&
                    methodCallExpr.getArguments().size() == 0)
                meetTestFunc = true;
            return super.visit(methodCallExpr, parserWriter);
        }

    }

    public class SplitVisitor extends ModifierVisitor<ParserWriter> {
        //private ArrayList<MethodDeclaration> splitMethods = new ArrayList<>();
        private Stack<NodeList<MethodDeclaration>> methodToAdd = new Stack<>();
        private int expectAssertNumber = 0;
        private int findAssertNumber = 0;
        private boolean ownAssert = false;
        private boolean meetTestFunc = false;
        private Set<String> assertFunctionSet;
        private Set<String> testFunctionSet;

        @Override
        public Visitable visit(final CompilationUnit cu, ParserWriter parserWriter){
            InspectVisitor inspector = new InspectVisitor();
            cu.accept(inspector, parserWriter);
            assertFunctionSet = inspector.getAssertFunctionSet();
            testFunctionSet = inspector.getTestFunctionSet();
            RemoveVisitor removeVisitor = new RemoveVisitor();
            removeVisitor.testFunctionSet = testFunctionSet;
            cu.accept(removeVisitor, parserWriter);
            return super.visit(cu, parserWriter);
        }

        @Override
        public Visitable visit(final ClassOrInterfaceDeclaration classOrInterfaceDeclaration, final ParserWriter parserWriter){
            methodToAdd.push(new NodeList<>());
            super.visit(classOrInterfaceDeclaration, parserWriter);
            NodeList<BodyDeclaration<?>> members = classOrInterfaceDeclaration.getMembers();
            NodeList<MethodDeclaration> newMethodList = methodToAdd.pop();
            members.addAll(newMethodList);
            classOrInterfaceDeclaration.setMembers(members);
            return classOrInterfaceDeclaration;
        }

        @Override
        public Visitable visit(final MethodDeclaration methodDeclaration, final ParserWriter parserWriter){
            //System.out.println("visit method " + methodDeclaration.getName().toString());
            //super.visit(methodDeclaration, parserWriter);
            //System.out.println("visit " + methodDeclaration.getName().toString());
            //boolean testFunction = false;
            //for(AnnotationExpr annotationExpr: methodDeclaration.getAnnotations()){
            //    if(annotationExpr.toString().equals("@Test")){
            //        testFunction = true;
            //        //System.out.println(methodDeclaration.getName().toString());
            //    }
            //}
            //if(testFunction){
            String name = methodDeclaration.getNameAsString();
            if(name.equals("testReflectionArrayCycleLevel2") ||
                    name.equals("testSetCauseToNull") ||
                    name.equals("testReadDeclaredNamedFiled") ||
                    name.equals("testReadDeclaredNamedFieldForceAccess") ||
                    name.equals("testReadDeclaredNamedStaticFieldForceAccess") ||
                    name.equals("testReadDeclaredNamedField") ||
                    name.equals("testReadDeclaredNamedStaticField") ||
                    name.equals("testReadNamedField") ||
                    name.equals("testBinaryIntMap")
            )
                return methodDeclaration;
            if(isTestMethod(methodDeclaration)){
                expectAssertNumber = 0;
                //findAssertNumber = 0;
                while(true){
                    findAssertNumber = 0;
                    expectAssertNumber += 1;
                    MethodDeclaration cloneMethod = methodDeclaration.clone();
                    cloneMethod.setName(methodDeclaration.getNameAsString() + "_split_"
                            + Integer.toString(expectAssertNumber));
                    //cloneMethod.accept(this, parserWriter);
                    super.visit(cloneMethod, parserWriter);
                    if( findAssertNumber >= expectAssertNumber ){
                        methodToAdd.peek().add(cloneMethod);
                    }else{
                        break;
                    }
                }
                //this situation, delete the former method.
                return null;
            }else{
                return methodDeclaration;
            }
        }

        @Override
        public Visitable visit(final ExpressionStmt expressionStmt, ParserWriter parserWriter){
            ownAssert = false;
            meetTestFunc = false;
            //expressionStmt.accept(this, parserWriter);
            super.visit(expressionStmt, parserWriter);
            if (ownAssert) {
                findAssertNumber += 1;
                if(findAssertNumber == expectAssertNumber){
                    return expressionStmt;
                } else{
                    //return new EmptyStmt();
                    return null;
                }
            } else if(meetTestFunc) {
                return null;
            }
            else{
                return expressionStmt;
            }
        }

        @Override
        public Visitable visit(final MethodCallExpr methodCallExpr, ParserWriter parserWriter){
            //System.out.println("call: " + methodCallExpr.getName().toString());
            //if(methodCallExpr.getParentNode().isPresent())
            //    System.out.println("father node: " + methodCallExpr.getParentNode().get().getClass());
            if(!ownAssert)
                ownAssert = isAssertCall(methodCallExpr);
            if(testFunctionSet.contains(methodCallExpr.getNameAsString()) &&
                    methodCallExpr.getArguments().size() == 0)
                meetTestFunc = true;
            return super.visit(methodCallExpr, parserWriter);
        }

        private boolean isAssertCall(MethodCallExpr methodCallExpr){
            //String callName = methodCallExpr.getName().toString();
            //return callName.indexOf("assert") == 0 ||
            //        callName.equals("fail");
            if(methodCallExpr.getArguments().size() != 0){
                return assertFunctionSet.contains(methodCallExpr.getNameAsString());
            }
            return false;
        }

        private boolean isTestMethod(MethodDeclaration methodDeclaration){
            //for(AnnotationExpr annotationExpr: methodDeclaration.getAnnotations()){
            //    if(annotationExpr.toString().equals("@Test")){
            //        return true;
            //        //System.out.println(methodDeclaration.getName().toString());
            //    }
            //}
            //return methodDeclaration.getName().toString().indexOf("test") == 0;
            if(methodDeclaration.getParameters().size() == 0)
                return testFunctionSet.contains(methodDeclaration.getNameAsString());
            return false;
        }
    }
}

