package com.sklcs.mainProject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.Node;

//import static com.github.javaparser.ParserConfiguration.LanguageLevel.*;

public class AddBordersParser extends AbstractParser {
    public AddBordersParser(String resultFile) throws IOException {
        //String[] header = new String[]{"type", "file", "start", "end"};
        //super(resultFile, header);
        super(resultFile, new String[]{"file", "type", "start", "end"}, 3);
    }

    @Override
    public void parse(String filePath) {
        try{
            //System.out.println(filePath);
            this.writer.setFileNow(filePath);
            FileInputStream fileInputStream = new FileInputStream(filePath);
            //StaticJavaParser.getConfiguration().setLanguageLevel(JAVA_1_4);
            //System.out.println(filePath);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            cu.accept(new BorderVisitor(), this.writer);
        }
        catch (FileNotFoundException e){
            System.out.println("file not found" + e);
        }

    }


    public static class BorderVisitor extends VoidVisitorAdapter<ParserWriter>{
        private static String startLine(Node node){
            if (node == null)
                return "-1";
            return Integer.toString(node.getRange().isPresent() ? node.getRange().get().startLine() : -1);
        }

        private static String endLine(Node node){
            if(node == null)
                return "-1";
            return Integer.toString(node.getRange().isPresent() ? node.getRange().get().endLine() : -1);
        }

        @Override
        public void visit(MethodDeclaration n, ParserWriter writer){
            //System.out.println("visit MethodDeclaration");
            String[] result = {"method", startLine(n), endLine(n)};
            writer.writeRow(result);
            super.visit(n, writer);
        }

        @Override
        public void visit(IfStmt ifStmt, ParserWriter writer){
            //System.out.println("visitIf");
            String[] result = {"if", startLine(ifStmt), endLine(ifStmt.getThenStmt())};
            writer.writeRow(result);
            if(ifStmt.getElseStmt().isPresent()){
                String[] elseResult = {"else", startLine(ifStmt.getElseStmt().get()),
                endLine(ifStmt.getElseStmt().get())};
                writer.writeRow(elseResult);
            }
            super.visit(ifStmt, writer);
        }

        @Override
        public void visit(WhileStmt whileStmt, ParserWriter writer){
            String[] result = {"while", startLine(whileStmt), endLine(whileStmt)};
            writer.writeRow(result);
            super.visit(whileStmt, writer);
        }

        @Override
        public void visit(ForStmt forStmt, ParserWriter writer){
            String[] result = {"for", startLine(forStmt), endLine(forStmt)};
            writer.writeRow(result);
            super.visit(forStmt, writer);
        }

        @Override
        public void visit(ForEachStmt forEachStmt, ParserWriter writer){
            String[] result = {"forEach", startLine(forEachStmt), endLine(forEachStmt)};
            writer.writeRow(result);
            super.visit(forEachStmt, writer);
        }

        @Override
        public void visit(SwitchStmt switchStmt, ParserWriter writer){
            String[] result = {"switch", startLine(switchStmt), endLine(switchStmt)};
            writer.writeRow(result);
            for(SwitchEntry switchEntry: switchStmt.getEntries()){
                String[] entry = {"switchEntry", startLine(switchEntry), endLine(switchEntry)};
                writer.writeRow(entry);
            }
            super.visit(switchStmt, writer);
        }

        @Override
        public void visit(TryStmt tryStmt, ParserWriter writer){
            String[] result = {"try", startLine(tryStmt), endLine(tryStmt.getTryBlock())};
            writer.writeRow(result);
            if(tryStmt.getFinallyBlock().isPresent()){
                String[] finallyBlock = {"finally", startLine(tryStmt.getFinallyBlock().get()),
                endLine(tryStmt.getFinallyBlock().get())};
                writer.writeRow(finallyBlock);
            }
            for(CatchClause catchClause: tryStmt.getCatchClauses()){
                String[] clause = {"catchClause", startLine(catchClause), endLine(catchClause)};
                writer.writeRow(clause);
            }
            super.visit(tryStmt, writer);
        }
    }
}
