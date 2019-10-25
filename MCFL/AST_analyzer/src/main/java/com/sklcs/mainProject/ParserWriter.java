package com.sklcs.mainProject;

import com.opencsv.CSVWriter;
import java.io.FileWriter;
import java.io.IOException;

public class ParserWriter {
    public String fileNow;
    private String[] header;
    private CSVWriter writer;
    private int min_length;
    public ParserWriter(String resultFile, String[] header, int min_length) throws IOException{
        this.fileNow = "";
        FileWriter fileWriter;
        if(!resultFile.endsWith(".csv")){
            resultFile = resultFile + ".csv";
            //System.out.println(resultFile);
        }
        fileWriter = new FileWriter(resultFile);
        this.writer = new CSVWriter(fileWriter);
        //String[] header = {"type", "file", "start", "end"};
        this.header = header;
        this.writer.writeNext(header);
        this.min_length = min_length;
    }

    public void setFileNow(String fileNow) {
        this.fileNow = fileNow;
    }

    public void writeRow(String[] toWrite){
        //System.out.println(toWrite.length);
        if(toWrite.length < this.min_length){
            return;
        }
        //String[] newRow = {toWrite[0], this.fileNow, toWrite[1], toWrite[2]};
        //this.writer.writeNext(newRow);

        if(this.header.length == this.min_length + 1){
            String [] newRow = new String[toWrite.length+1];
            newRow[0] = this.fileNow;
            for(int i =0; i!=toWrite.length; i++)
                newRow[i+1] = toWrite[i];
            this.writer.writeNext(newRow);
        } else{
            this.writer.writeNext(toWrite);
        }

    }

    public void close() throws IOException{
        this.writer.close();
    }
}
