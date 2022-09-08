ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
COPY start.sh /
RUN chmod a+x /start.sh

CMD [ "/start.sh" ]
