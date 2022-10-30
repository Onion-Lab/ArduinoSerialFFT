clear all; close all; clc;

array=readmatrix('eegtest.csv'); %뇌파측정데이터 csv연결

fs =512; %Neurosky 샘플링 주파수
t = 0:1:511; %샘플링할 주파수 개수(시간범위를 1~400초)
x=array(:,1); %fft변환전 raw데이터 들의 수치값 즉, 뇌파의 파형

X=fft(x); %raw데이터를 고속푸리에 변환

N=length(x); %입력함수의 총길이
n=0:N-1;
f=fs*n/N;  %주파수 축 (푸리에 변환식에 따라)

plot(abs(X))

%로우데이터는 음의값또한 가지기 때문에 power를 반반씩 나누어 먹으므로 2를곱합
%그리고 그래프가 중앙을 중심으로 대칭하는 모습을 띄기때문에

%cutoff=ceil(N/2); %대칭되는 부분을 다 볼필요없기에 실링(반올림)
%X=X(1:cutoff);
%f=f(1:cutoff);

%plot(f,2*abs(X)/N); %y축 크기가 시간의 길이에 영향을 받기때문에 N으로 나눔

