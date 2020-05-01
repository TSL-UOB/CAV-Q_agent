% Plot test generation accuracy for each method

figure(1); clf; hold on
plot(RA.Time,RA.Accuracy)
plot(RB.Time,RB.Accuracy)
plot(PR.Time,PR.Accuracy)
plot(EL.Time,EL.Accuracy)
plot(QA.Time,QA.Accuracy)

ylabel("Accuracy (%)")
xlabel("Simulation Time (ticks)")
legend('Random','Constrained','Proximity','Election','Q-Agent','Location','Best')
title("Test generation accuracy over 50 episodes")

%%
% Create gif of same data
numberOfFrames = 471;
allTheFrames = cell(numberOfFrames,1);
vidHeight = 344;
vidWidth = 446;
allTheFrames(:) = {zeros(vidHeight, vidWidth, 3, 'uint8')};
allTheColorMaps = cell(numberOfFrames,1);
allTheColorMaps(:) = {zeros(256, 3)};
myMovie = struct('cdata', allTheFrames, 'colormap', allTheColorMaps);
set(gcf, 'renderer', 'zbuffer');


h = figure(2); clf;
axis tight manual % this ensures that getframe() returns a consistent size
filename = 'accuracy';
for n = 1:472
    % Draw plot for y = x.^n
    x =data.Time(1:n);
    y =data{1:n,2:6};
    plot(x,y), xlim([0 500]); ylim([0 100]);
    ylabel("Accuracy (%)")
    xlabel("Simulation Time (ticks)")
    legend('Random','Constrained','Proximity','Election','Q-Agent','Location','southeast')
    title("Test generation accuracy over 50 episodes")
    drawnow 
    F(n) = getframe(gcf);
end
%%
vidFile = strcat(filename,'.avi');
v = VideoWriter(vidFile);
% v = VideoWriter(filename,'MPEG-4');
v.FrameRate=25;
open(v)
writeVideo(v,F)
close(v)
disp('exporting video...complete');
