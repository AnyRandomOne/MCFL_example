package com.sklcs.mainProject;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.stmt.Statement;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.*;

public class VariableParser extends AbstractParser {
    Map<String, Set<String>> variableUseDict;
    //private String packageName;

    VariableParser(String resultFile) throws IOException {
        super(resultFile, headlines(), 2);
        this.variableUseDict = new HashMap<>();
    }

    protected static String[] headlines(){
        return new String[]{"line", "variable"};
    }

    @Override
    public void parse(ArrayList<String> filePathArray) {
        for (String fileName : filePathArray) {
            parse(fileName);
        }
        writeResult();
    }

    private void writeResult(){
        for(String lineName: variableUseDict.keySet()){
            String variableNames = String.join(";", variableUseDict.get(lineName));
            writer.writeRow(new String[] {lineName, variableNames});
        }
    }

    @Override
    public void parse(String filePath) {
        try {
            FileInputStream fileInputStream = new FileInputStream(filePath);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            NameVisitor nameVisitor = new NameVisitor();
            nameVisitor.setFileName(filePath);
            cu.accept(nameVisitor, this.variableUseDict);
        } catch (Exception e) {
            System.out.println("error: " + e);
        }
    }


}
