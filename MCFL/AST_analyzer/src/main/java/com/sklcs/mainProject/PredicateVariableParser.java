package com.sklcs.mainProject;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;

import java.io.FileInputStream;
import java.io.IOException;

public class PredicateVariableParser extends VariableParser {
    PredicateVariableParser(String resultFile) throws IOException{
        super(resultFile);
    }

    @Override
    public void parse(String filePath) {
        try {
            FileInputStream fileInputStream = new FileInputStream(filePath);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            PredicateNameVisitor predicateNameVisitor = new PredicateNameVisitor();
            predicateNameVisitor.setFileName(filePath);
            cu.accept(predicateNameVisitor, this.variableUseDict);
        } catch (Exception e) {
            System.out.println("error: " + e);
        }
    }
}
