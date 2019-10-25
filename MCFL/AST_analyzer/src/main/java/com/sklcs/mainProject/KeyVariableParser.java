package com.sklcs.mainProject;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;

import java.io.FileInputStream;
import java.io.IOException;

public class KeyVariableParser extends PredicateVariableParser {
    KeyVariableParser(String resultFile) throws IOException{
        super(resultFile);
    }

    @Override
    public void parse(String filePath) {
        try {
            FileInputStream fileInputStream = new FileInputStream(filePath);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            KeyVariableNameVisitor predicateNameVisitor = new KeyVariableNameVisitor();
            predicateNameVisitor.setFileName(filePath);
            cu.accept(predicateNameVisitor, this.variableUseDict);
        } catch (Exception e) {
            System.out.println("error: " + e);
        }
    }
}